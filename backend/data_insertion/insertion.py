import os
import glob
import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from openai import OpenAI
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Initialize OpenAI client (fixed the API key issue)
client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

def get_embedding(text, model=embedding_model):
    """Generate embedding for text using OpenAI API"""
    try:
        text = text.replace("\n", " ")
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks for better vector search"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks

def find_all_pdf_files(data_folder: str) -> List[str]:
    """Find all PDF files in the data folder recursively"""
    pdf_pattern = os.path.join(data_folder, "**", "*.pdf")
    pdf_files = glob.glob(pdf_pattern, recursive=True)
    return pdf_files

def create_collection_if_not_exists():
    """Create Qdrant collection if it doesn't exist"""
    try:
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if COLLECTION_NAME not in collection_names:
            print(f"Creating collection: {COLLECTION_NAME}")
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
            print(f"Collection '{COLLECTION_NAME}' created successfully")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists")
    except Exception as e:
        print(f"Error creating collection: {e}")

def process_pdf_file(pdf_path: str, base_folder: str) -> List[Dict[str, Any]]:
    """Process a single PDF file and return chunks with metadata"""
    print(f"Processing: {pdf_path}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"No text extracted from {pdf_path}")
        return []
    
    # Chunk the text
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks from {pdf_path}")
    
    # Prepare data for Qdrant
    points_data = []
    relative_path = os.path.relpath(pdf_path, base_folder)
    
    for i, chunk in enumerate(chunks):
        if chunk.strip():  # Only process non-empty chunks
            # Generate embedding
            embedding = get_embedding(chunk)
            if embedding:
                point_data = {
                    'id': str(uuid.uuid4()),
                    'vector': embedding,
                    'payload': {
                        'text': chunk,
                        'source_file': relative_path,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'file_type': 'pdf'
                    }
                }
                points_data.append(point_data)
    
    return points_data

def insert_points_to_qdrant(points_data: List[Dict[str, Any]], batch_size: int = 100):
    """Insert points to Qdrant in batches"""
    if not points_data:
        return
    
    print(f"Inserting {len(points_data)} points to Qdrant...")
    
    # Process in batches
    for i in tqdm(range(0, len(points_data), batch_size), desc="Inserting batches"):
        batch = points_data[i:i + batch_size]
        
        # Convert to PointStruct objects
        points = [
            PointStruct(
                id=point['id'],
                vector=point['vector'],
                payload=point['payload']
            )
            for point in batch
        ]
        
        try:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                wait=True,
                points=points,
            )
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {e}")

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=qdrant_url, 
    api_key=qdrant_api_key,
)

def main():
    """Main function to process all PDF files and insert into Qdrant"""
    print("Starting PDF to Qdrant insertion process...")
    
    # Create collection if it doesn't exist
    create_collection_if_not_exists()
    
    # Find all PDF files
    data_folder = "data_insertion/data"

    pdf_files = find_all_pdf_files(data_folder)
    
    if not pdf_files:
        print("No PDF files found in the data folder")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process all PDF files
    all_points_data = []
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDF files"):
        try:
            points_data = process_pdf_file(pdf_file, data_folder)
            all_points_data.extend(points_data)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            continue
    
    print(f"Total points to insert: {len(all_points_data)}")
    
    # Insert all points to Qdrant
    if all_points_data:
        insert_points_to_qdrant(all_points_data)
        print("PDF insertion to Qdrant completed successfully!")
    else:
        print("No data to insert")

# Run the main function
if __name__ == "__main__":
    main()

