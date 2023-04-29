import json
from dataclasses import dataclass

import base58
import gql.transport.exceptions as gql_exceptions
import grpc
import multiaddr
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport
from graphql import DocumentNode

from .api import api_pb2, api_pb2_grpc

# TODO error handling

ROUTE_GRAPHQL = "graphql"
ROUTE_SCHEMA_LOAD = "schema/load"
ROUTE_PEERID = "peerid"


@dataclass
class DefraConfig:
    """
    Configuration for DefraDB client.
    """

    api_url: str = "localhost:9181/api/v0"
    rpc_url: str = "localhost:9161"
    scheme = "http://"


class DefraClient:
    """
    Client for DefraDB, providing methods for interacting with the DefraDB node.
    Most interactions with DefraDB are via the graphql endpoint, using the Defra query language,
    by passing a valid gql object.

    Synchronous.
    """

    url = None
    gql_sync_transport = None
    gql_async_transport = None

    def __init__(self, cfg):
        self.cfg: DefraConfig = cfg
        url = f"{self.cfg.scheme}{self.cfg.api_url}{ROUTE_GRAPHQL}"
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
            raise Exception("Failed to execute graphql request", e)
        return response

    def load_schema(self, schema: str) -> dict | None:
        """
        Load a schema into the DefraDB node.
        """
        url = f"{self.cfg.scheme}{self.cfg.api_url}{ROUTE_SCHEMA_LOAD}"
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
        url = f"{self.cfg.scheme}{self.cfg.api_url}{ROUTE_PEERID}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to get peerid", response.text)
        return response.json()["data"]["peerID"]

    def set_collection_replication(self, collectionName: str, peerURL: str):
        pass

    def get_all_replicators(self):
        pass


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


def update_mutation_from_dict(schema_type: str, data: dict) -> DocumentNode:
    """
    Create a mutation to create a new document of a specific type.
    """
    data_json = json.dumps(data, ensure_ascii=False).replace('"', '\\"')
    request_string = f"""
        mutation {{
            update_{schema_type}(data: "{data_json}") {{
                _key
            }}
        }}
    """
    return gql(request_string)
