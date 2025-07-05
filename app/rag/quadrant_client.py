from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv("QUADRANT_URL"),
    api_key=os.getenv("QUADRANT_API_KEY"),
)

# print(qdrant_client.get_collection("test"))