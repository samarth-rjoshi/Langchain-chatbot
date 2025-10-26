import os
from typing import TypedDict, List
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

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
class GraphState(TypedDict):
    query: str
    retrieved_docs: List[dict]
    answer: str


def retrieve(state: GraphState) -> GraphState:
    """
    Retrieve relevant documents from Qdrant based on the query.
    Uses functions from data_insertion folder.
    """
    print(f"Retrieving documents for query: {state['query']}")

    query = state['query']
    results = query_documents(query=query)
    state['retrieved_docs'] = results
    return state


def generate(state: GraphState) -> GraphState:
    """
    Generate an answer based on the query and retrieved documents.
    """
    print(f"Generating answer...")
    
    query = state['query']
    retrieved_docs = state['retrieved_docs']
    try:
    
        context = "\n\n".join(retrieved_docs)

        prompt = f"""Based on the following context, please answer the question.

    Context:
    {context}

    Question: {query}

    Answer:"""
        breakpoint()
        response = llm.invoke(prompt)
        state['answer'] = response.content
        return state
    except Exception as e:
        print(f"Error generating answer: {e}")
        state['answer'] = "Sorry, I encountered an error while generating the answer."
        return state

    


    


def create_graph() -> StateGraph:
    """
    Create and return the LangGraph with retrieve and generate nodes.
    """
    # Create a new graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    
    # Define the flow: START -> retrieve -> generate -> END
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    # Compile and return the graph
    app = workflow.compile()
    return app


def run_query(query: str) -> dict:
    """
    Execute the graph with a given query.
    
    Args:
        query: The user's question
        
    Returns:
        The final state containing the answer
    """
    # Create the graph
    app = create_graph()
    
    # Initial state
    initial_state = GraphState(
        query=query,
        retrieved_docs=[],
        answer=""
    )
    
    # Run the graph
    result = app.invoke(initial_state)
    
    return result


if __name__ == "__main__":
    # Example usage
    query = "What is LangChain?"
    result = run_query(query)
    print("\n" + "="*50)
    print("Query:", result['query'])
    print("\nAnswer:", result['answer'])
    print("="*50)

