import os
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

def langgraph_collection():
    """
    Returns a MongoDBSaver instance connected to the configured MongoDB.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set")
    
    client = MongoClient(mongo_uri)
    # Use a specific database for langgraph checkpoints, e.g., 'langgraph_checkpoints'
    # or the same database as the app if preferred. Here we use 'langgraph'.
    checkpointer = MongoDBSaver(client)
    return checkpointer
