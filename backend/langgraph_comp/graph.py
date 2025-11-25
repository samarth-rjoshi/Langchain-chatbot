import os
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import re
from db_connect import langgraph_collection

# Import functions from data_insertion folder
from data_insertion.db_operations import query_documents
from data_insertion.insertion import qdrant_client
from logging_config import get_logger

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
    messages: Annotated[List[BaseMessage], add_messages]
    headline: str


logger = get_logger(__name__)


def retrieve(state):
    """
    Retrieve relevant documents from Qdrant based on the query.
    Uses functions from data_insertion folder.
    """
    print(f"DEBUG: Retrieving documents for query: {state.get('query')}")
    logger.info("Retrieving documents for query: %s", state.get('query'))

    query = state['query']
    results = query_documents(query=query)
    state['retrieved_docs'] = results
    return state


def generate(state):
    """
    Generate an answer based on the query and retrieved documents.
    """
    print("DEBUG: Generating answer...")
    logger.info("Generating answer...")
    
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
        
        # Update messages
        # We return the NEW messages to be added
        output = {
            "answer": clean_text,
            "messages": [
                HumanMessage(content=query),
                AIMessage(content=clean_text) # Or [clean_text, retrieved_docs] if we want to store docs
            ]
        }
        print(f"DEBUG: Generate output: {output}")
        return output
    except Exception as e:
        logger.exception("Error generating answer: %s", e)
        print(f"DEBUG: Error generating answer: {e}")
        state['answer'] = "Sorry, I encountered an error while generating the answer."
        return state

def generate_headline(state):
    """
    Generate a short headline based on the user query.
    """
    # Only generate if not already present or if it's the default
    # Since we don't have easy access to the "previous" state here without checkpointer logic inside the node,
    # we can check if 'headline' is in state. 
    # However, for a new turn, state might be merged.
    # Let's just generate it based on the query. The app.py can decide whether to save it or not.
    # Or better, we generate it and return it.
    
    query = state['query']
    try:
        prompt = f"Generate a very short, concise headline (max 5 words) for this user query. Do not use quotes. Query: {query}"
        response = llm.invoke(prompt)
        headline = response.content.strip().replace('"', '')
        return {"headline": headline}
    except Exception as e:
        logger.error(f"Error generating headline: {e}")
        return {"headline": "Conversation"}

# Initialize checkpointer
checkpointer = langgraph_collection()

langchain_graph = (
    StateGraph(State)
    .add_node("retrieve", retrieve)
    .add_node("generate", generate)
    .add_node("generate_headline", generate_headline)
    .add_edge(START, "retrieve")
    .add_edge(START, "generate_headline")
    .add_edge("retrieve", "generate")
    .add_edge("generate", END)
    .add_edge("generate_headline", END)
    .compile(checkpointer=checkpointer)
)






