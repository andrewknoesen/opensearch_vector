from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json

# Get the domain endpoint from CDK outputs
host = 'search-vector-store-demo-o6bhj7main53jjygept3xsivey.af-south-1.es.amazonaws.com'  # without https://
region = 'af-south-1'  # e.g., 'af-south-1'

# For testing with basic auth (use IAM auth for production)
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=('admin', 'YourStrongPassword123!'),  # Use the credentials you set
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Create index with KNN mapping for vector embeddings
index_name = "vector-index"
index_body = {
    "settings": {
        "index.knn": True
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "text": {"type": "text"},
            "vector_embedding": {
                "type": "knn_vector",
                "dimension": 1536  # Adjust based on your embedding model
            }
        }
    }
}

# Create the index
response = client.indices.create(index=index_name, body=index_body)
print(f"Index creation response: {response}")
