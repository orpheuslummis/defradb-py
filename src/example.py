# A minimal example of how to use DefraClient.

import uuid
from gql import gql
from defradb.defradb import (
    DefraClient,
    DefraConfig,
    create_mutation_from_dict,
)

# Configuring the client.
endpoint = "http://localhost:9181/api/v0/"
config = DefraConfig(endpoint)
client = DefraClient(config)

# Loading a schema as a string.
typename = "Parameters"
schema = f"""
type {typename} {{
    a: String
    b: String
    c: String
}}
"""
response_schema = client.load_schema(schema)

# Creating a new document of the type with random data.
data = {
    "a": uuid.uuid4().hex,
    "b": uuid.uuid4().hex,
    "c": uuid.uuid4().hex,
}
request = create_mutation_from_dict(typename, data)
response_mutation = client.request(request)

# Obtaining a list of all these documents.
get_users_request = gql(
    f"""
query {{
    {typename} {{
        _key
        a
        b
        c
    }}
}}
"""
)
response_users = client.request(get_users_request)
if response_users is not None:
    for user in response_users:
        print(user)
