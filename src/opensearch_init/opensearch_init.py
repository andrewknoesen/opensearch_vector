import json
from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3

APP_NAME = "vector-store-demo"
REGION = "af-south-1"
SESSION = boto3.Session(profile_name="personal", region_name=REGION)
SSM_CLIENT = SESSION.client("ssm")
# host = 'search-vector-store-demo-o6bhj7main53jjygept3xsivey.af-south-1.es.amazonaws.com'  # without https://


def get_secret() -> str:
    secrets_client = SESSION.client(service_name="secretsmanager")
    secret_response = secrets_client.get_secret_value(
        SecretId=SSM_CLIENT.get_parameter(Name=f"/{APP_NAME}/opensearch-secret-arn")["Parameter"]["Value"]
    )
    secret = secret_response["SecretString"]
    return json.loads(secret)


def main():
    host = SSM_CLIENT.get_parameter(Name=f"/{APP_NAME}/opensearch-endpoint")["Parameter"]["Value"]
    # For testing with basic auth (use IAM auth for production)
    login_details = get_secret()
    client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=(login_details["username"], login_details["password"]),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    # Create index with KNN mapping for vector embeddings
    index_name = "vector-index"
    index_body = {
        "settings": {"index.knn": True},
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "text": {"type": "text"},
                "vector_embedding": {
                    "type": "knn_vector",
                    "dimension": 1536,  # Adjust based on your embedding model
                },
            }
        },
    }

    # Create the index
    return client.indices.create(index=index_name, body=index_body)


if __name__ == "__main__":
    print("Index creation started...")
    response = main()
    print(f"Index creation response: {response}")
