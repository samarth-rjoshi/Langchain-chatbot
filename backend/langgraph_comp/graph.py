import os
from typing import TypedDict, List
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import re


# Import functions from data_insertion folder
from data_insertion.db_operations import query_documents
from data_insertion.insertion import qdrant_client

load_dotenv()

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
GENERATION_MODEL = os.getenv("GENERATION_MODEL")

# Initialize OpenAI client
openai_client = OpenAI(base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

llm = ChatOpenAI(model=GENERATION_MODEL, base_url=OPENAI_API_BASE, api_key=OPENAI_API_KEY)


# Define the state schema
class State(TypedDict):
    query: str
    retrieved_docs: List[dict]
    answer: str


def retrieve(state):
    """
    Retrieve relevant documents from Qdrant based on the query.
    Uses functions from data_insertion folder.
    """
    print(f"Retrieving documents for query: {state['query']}")

    query = state['query']
    results = query_documents(query=query)
    state['retrieved_docs'] = results
    return state


def generate(state):
    """
    Generate an answer based on the query and retrieved documents.
    """
    print(f"Generating answer...")
    
    query = state['query']
    retrieved_docs = state['retrieved_docs']
    try:
    

        prompt = f"""Based on the following context, please answer the question.

    Context:
    {retrieved_docs}

    Question: {query}

    Answer:"""
        
        response = llm.invoke(prompt)
        clean_text = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
        state['answer'] = clean_text
        return state
    except Exception as e:
        print(f"Error generating answer: {e}")
        state['answer'] = "Sorry, I encountered an error while generating the answer."
        return state

langchain_graph = (
    StateGraph(State)
    .add_node("retrieve", retrieve)
    .add_node("generate", generate)
    .add_edge(START, "retrieve")
    .add_edge("retrieve", "generate")
    .add_edge("generate", END)
    .compile()
)





