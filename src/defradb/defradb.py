import json
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport
import gql.transport.exceptions as gql_exceptions
from graphql import DocumentNode

import requests
from urllib.parse import urljoin

# TODO error handling

ROUTE_GRAPHQL = "graphql"
ROUTE_SCHEMA_LOAD = "schema/load"
ROUTE_PEERID = "peerid"


class DefraConfig:
    """
    Configuration for DefraDB client.
    """

    api_url: str

    def __init__(self, api_url):
        self.api_url = api_url


class DefraClient:
    """
    Client for DefraDB, providing methods for interacting with the DefraDB node.
    Most interactions with DefraDB are via the graphql endpoint, using the Defra query language,
    by passing a valid gql object.
    """

    def __init__(self, config):
        self.config: DefraConfig = config
        url = urljoin(config.api_url, ROUTE_GRAPHQL)
        self.gql_sync_transport = RequestsHTTPTransport(url=url)
        self.gql_async_transport = AIOHTTPTransport(url=url)

    def request(self, request: DocumentNode) -> dict | None:
        """
        Execute a graphql request against the DefraDB node.
        """
        response = None
        client = Client(
            transport=self.gql_sync_transport, fetch_schema_from_transport=False
        )
        try:
            response = client.execute(request)
        except gql_exceptions.TransportQueryError as e:
            # FIXME temporary issue with defradb
            if e.errors != [{}]:
                raise Exception("Failed to execute query", e.errors)
        return response

    async def request_async(self, request: DocumentNode) -> dict | None:
        """
        Execute an async graphql request against the DefraDB node.
        """
        client = Client(
            transport=self.gql_async_transport, fetch_schema_from_transport=False
        )
        async with client as session:
            response = await session.execute(request)
            return response

    def load_schema(self, schema: str) -> dict | None:
        """
        Load a schema into the DefraDB node.
        """
        url = urljoin(self.config.api_url, ROUTE_SCHEMA_LOAD)
        response = requests.post(url, data=schema)
        response_json = response.json()
        if "errors" in response_json:
            for error in response_json["errors"]:
                if "schema type already exists" not in error["message"]:
                    raise Exception("Failed to load schema", error)
        return response_json

    def get_peerid(self) -> str:
        """
        Get the peerid of the DefraDB node.
        """
        url = urljoin(self.config.api_url, ROUTE_PEERID)
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to get peerid", response.text)
        return response.json()["data"]["peerID"]


def create_mutation_from_dict(schema_type: str, data: dict) -> DocumentNode:
    """
    Create a mutation to create a new document of a specific type.
    """
    data_json = json.dumps(data, ensure_ascii=False).replace('"', '\\"')
    request_string = f"""
        mutation {{
            create_{schema_type}(data: "{data_json}") {{
                _key
            }}
        }}
    """
    return gql(request_string)
