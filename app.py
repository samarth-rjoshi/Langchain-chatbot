import os
import streamlit as st
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Environment Variables
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN", "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")
QDRANT_URL = "https://ff0ebcb9-0815-4aee-8810-f3cdff8c1dd5.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzQzMDY0NjI4fQ.jp5Zjt5LhyA_gWQTefoREQbOFyeShNoWyqkQFnYoOnI"
COLLECTION_NAME = "langchain"

# Initialize Qdrant Client with API Key
try:
    client = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)  
    if not client.collection_exists(COLLECTION_NAME):
        st.error(f"Collection '{COLLECTION_NAME}' not found. Create it first.")
        st.stop()
except Exception as e:
    st.error(f"Error connecting to Qdrant: {e}")
    st.stop()

# ✅ Load Embeddings Model Properly
try:
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    st.error(f"Error loading embedding model: {e}")
    st.stop()

# ✅ Ensure Qdrant is Initialized with Embeddings
try:
    qdrant_db = Qdrant(
        client=client, 
        collection_name=COLLECTION_NAME, 
        embeddings=embedding_model  # ✅ Fix: Pass embeddings instead of embedding_function
    )
except Exception as e:
    st.error(f"Error initializing Qdrant VectorStore: {e}")
    st.stop()

# Load Hugging Face Model
try:
    llm = HuggingFaceHub(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        model_kwargs={"temperature": 0.7, "max_length": 512},
        huggingfacehub_api_token=HUGGINGFACE_API_KEY
    )
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# Conversation Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Chat Chain
retrieval_chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=qdrant_db.as_retriever(), memory=memory
)

# Streamlit UI
st.title("Langchain Chatbot")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_input = st.text_input("You:", key="input")

if user_input:
    response = retrieval_chain.invoke({"question": user_input, "chat_history": st.session_state["chat_history"]})
    st.session_state["chat_history"].append((user_input, response["answer"]))

    for q, a in st.session_state["chat_history"]:
        st.write(f"**You:** {q}")
        st.write(f"**Bot:** {a}")
