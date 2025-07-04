import streamlit as st
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.llms import HuggingFaceHub
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
qdrant_langchain_url = os.getenv("QDRANT_LANGCHAIN_URL")
qdrant_langchain_api_key = os.getenv("QDRANT_LANGCHAIN_API_KEY")
qdrant_haystack_url = os.getenv("QDRANT_HAYSTACK_URL")
qdrant_haystack_api_key = os.getenv("QDRANT_HAYSTACK_API_KEY")

# Set environment variable for HuggingFaceHub API
os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_token

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize Qdrant clients
qdrant_client_langchain = QdrantClient(
    url=qdrant_langchain_url,
    api_key=qdrant_langchain_api_key
)

qdrant_client_haystack = QdrantClient(
    url=qdrant_haystack_url,
    api_key=qdrant_haystack_api_key
)

# Initialize Qdrant vector stores
qdrant_langchain = Qdrant(
    client=qdrant_client_langchain,
    collection_name="langchain",
    embeddings=embeddings
)

qdrant_haystack = Qdrant(
    client=qdrant_client_haystack,
    collection_name="my_collections",
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
            "You are an expert in LangChain and Haystack, frameworks for building applications with large language models. Your task is to answer questions with the utmost accuracy, providing clear and detailed explanations. When relevant, include code sequences to illustrate your points and guide users effectively. Your responses should be informative, concise, and geared towards helping users understand and apply LangChain and Haystack concepts and techniques.\n\n{context}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Create the document chain
document_chain = create_stuff_documents_chain(llm, question_answering_prompt)

# Streamlit app setup
st.set_page_config(page_title="LangChain & Haystack Chatbot", page_icon="🤖", layout="centered")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Layout for the Streamlit app
st.title('LangChain & Haystack Chatbot')

# Display chat history
for chat in st.session_state['chat_history']:
    if chat['role'] == 'user':
        st.markdown(f"**User:** {chat['content']}")
    else:
        st.markdown(f"**Assistant:** {chat['content']}")

# User input
query = st.text_input('Enter your query:', '')

# Documentation selection
doc_selection = st.selectbox('Select Documentation', ['LangChain', 'Haystack'])

if st.button('Send'):
    if query:
        # Add user message to chat history
        st.session_state['chat_history'].append({'role': 'user', 'content': query})

        # Initialize ephemeral chat history for the current interaction
        demo_ephemeral_chat_history = ChatMessageHistory()
        demo_ephemeral_chat_history.add_user_message(query)

        # Perform the similarity search based on user selection
        if doc_selection == 'LangChain':
            context = qdrant_langchain.similarity_search(query)
        else:
            context = qdrant_haystack.similarity_search(query)

        # Invoke the document chain with messages and context
        response = document_chain.invoke(
            {
                "messages": demo_ephemeral_chat_history.messages,
                "context": context,
            }
        )

        # Extract and display only the Assistant's message
        if 'Assistant:' in response:
            assistant_message = response.split('Assistant:')[-1].strip()
            st.session_state['chat_history'].append({'role': 'assistant', 'content': assistant_message})
            st.experimental_rerun()
        else:
            st.write("No valid response received.")
    else:
        st.write("Please enter a query.")
