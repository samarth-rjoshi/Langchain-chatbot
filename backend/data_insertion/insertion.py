import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct

from openai import OpenAI
load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")


client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_BASE)

def get_embedding(text, model=embedding_model):
   text = text.replace("\n", " ")
   return client.embeddings.create(input=[text], model=model).data[0].embedding

embeddings = get_embedding("Once upon a time, there was a cat.")

qdrant_client = QdrantClient(
    url=qdrant_url, 
    api_key=qdrant_api_key,
)
qdrant_client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)
points = [
    PointStruct(id=1, vector=embeddings, payload={"text": "Once upon a time, there was a cat."})

]
qdrant_client.upsert(
    collection_name=COLLECTION_NAME,
    wait=True, # Wait for the operation to complete
    points=points,
)

