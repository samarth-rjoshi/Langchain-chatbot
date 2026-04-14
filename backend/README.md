# LangChain Chatbot Backend

This directory contains the backend for the LangChain Chatbot. The backend is built in Python using Flask, LangChain, LangGraph, and Qdrant for Retrieval-Augmented Generation (RAG). It interacts with custom/local LLM models via OpenAI-compatible endpoints (e.g., LM Studio).

## 🚀 Setup & Installation

1. **Virtual Environment**: 
   Ensure you have a Python `>3.12` environment. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. **Environment Variables**:
   Create or modify the `.env` file in this directory with your configuration:
   ```env
   QDRANT_URL=<your-qdrant-url>
   QDRANT_API_KEY=<your-qdrant-api-key>
   EMBEDDING_MODEL=text-embedding-bge-m3
   

   OPENAI_API_KEY=
   OPENAI_API_BASE=
   GENERATION_MODEL=
   
   MONGO_URI=
   LANGSMITH_TRACING=true
   LANGSMITH_ENDPOINT=
   LANGSMITH_API_KEY=
   ```

## 🗄️ Ingesting Data into Qdrant

If you have new PDF files to be embedded and ingested into the vector database:

1. Place your PDFs into the `data_insertion/data` folder.
2. Run the insertion script. It will extract, chunk, embed, and push the documents to your configured Qdrant cluster:
   ```bash
   python -m data_insertion.insertion
   ```

## ⚙️ Running the API Server

The backend is exposed via a Flask application (located in the `api` directory) that interfaces with the LangGraph state graph.

To run the backend server:
```bash
python main.py
```
> The server typically runs on port 8000. It manages authentication, chat history logic, and stateful interactions with the LLM.

## 🧪 Running LangSmith Evaluations

We have local evaluation workflows set up using **LangSmith's LLM-as-a-judge**. This evaluates the RAG accuracy, relevance, and hallucination footprint against your documents.

### How to Evaluate
1. Make sure your local endpoint (e.g., LM studio) and your Qdrant instance are reachable.
2. Run the evaluator module:
   ```bash
   python -m evaluators.evaluate_rag
   ```

### Evaluation Targets
The script tests your actual LangGraph `agent/rag_bot` process against the `Langchain Concepts RAG Evaluation` dataset and outputs the results to LangSmith using 4 different metrics:
- **Correctness**
- **Relevance**
- **Groundedness**
- **Retrieval Relevance**

*(To modify the evaluation dataset, metrics, or instructions, edit `evaluators/evaluate_rag.py`).*
