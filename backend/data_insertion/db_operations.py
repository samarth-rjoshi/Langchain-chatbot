from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Initialize clients
client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def create_embedding(text, model=embedding_model):
    """Generate embedding for text using OpenAI API"""
    try:
        text = text.replace("\n", " ")
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def query_documents(query):
    
    try:
        query_vector = create_embedding(query)
        if not query_vector:
            return None

        results = []
        
        result = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            with_payload=["text"],
            limit=5
        )
        for point in result.points:
            results.append(point.payload["text"])

        return results
    except Exception as e:
        print(f"Error querying documents: {e}")
        return None
    
    
    