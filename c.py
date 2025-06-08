import streamlit as st
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.llms import HuggingFaceHub
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
import os

# Read environment variables from .env file
def load_env_file(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Load environment variables
load_env_file('.env')

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize Qdrant client
url_qdrant = os.getenv('QDRANT_URL')
api_key_qdrant = os.getenv('QDRANT_API_KEY')
collection_name = os.getenv('COLLECTION_NAME')
qdrant_client = QdrantClient(url=url_qdrant, api_key=api_key_qdrant)

# Initialize Qdrant vector store
qdrant_db = Qdrant(
    client=qdrant_client,
    collection_name=collection_name,
    embeddings=embeddings
)

# Initialize the LLM
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    model_kwargs={"temperature": 0.5, "max_length": 1024, "max_new_tokens": 1024}
)

# Define the prompt template
question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert in LangChain, a framework for building applications with large language models.\n"
            "Your task is to answer questions accurately, providing clear and detailed explanations.\n"
            "Include relevant code snippets when necessary.\n\n"
            "{context}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Create the document chain
document_chain = create_stuff_documents_chain(llm, question_answering_prompt)

# Streamlit app setup
st.set_page_config(page_title="DOC_U_CHAT A LangChain Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .stTextInput>div>div>input {
            border-radius: 20px;
            padding: 10px;
            border: 1px solid #ccc;
        }
        .stButton>button {
            border-radius: 20px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            color: #333;
        }
        .user-message {
            background-color: #e6f7ff;
            border: 1px solid #b3e5fc;
        }
        .assistant-message {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
        }
        .chat-message b {
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

st.title('DOC_U_CHAT A LangChain Chatbot 🤖')

st.markdown("""
This application is designed to help you understand and apply LangChain concepts. 
Enter your query, and get detailed explanations along with relevant code snippets.
""")

# Display chat history
for chat in st.session_state['chat_history']:
    if chat['role'] == 'user':
        st.markdown(f"<div class='chat-message user-message'><b>You:</b> {chat['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-message assistant-message'><b>Assistant:</b> {chat['content']}</div>", unsafe_allow_html=True)

# User input
query = st.text_input('Enter your query:', '', key="query_input", placeholder="Type your question here...")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button('Send', key="send_button"):
        if query:
            # Add user message to chat history
            st.session_state['chat_history'].append({'role': 'user', 'content': query})

            # Initialize ephemeral chat history
            ephemeral_chat_history = ChatMessageHistory()
            ephemeral_chat_history.add_user_message(query)

            # Perform similarity search
            context = qdrant_db.similarity_search(query)

            # Invoke the document chain with messages and context
            response = document_chain.invoke(
                {
                    "messages": ephemeral_chat_history.messages,
                    "context": context,
                }
            )

            # Extract and display the assistant's response
            assistant_message = response.strip()
            st.session_state['chat_history'].append({'role': 'assistant', 'content': assistant_message})

            # Clear the input field by rerunning the app
            st.experimental_rerun()
        else:
            st.write("Please enter a query.")
with col2:
    if st.button('Clear Chat', key="clear_button"):
        st.session_state['chat_history'] = []
        st.experimental_rerun()