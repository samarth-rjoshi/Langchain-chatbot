# Langchain Chatbot API

Flask-based REST API for the Langchain chatbot that integrates with LangGraph.

## Features

- **POST /chat**: Main endpoint for chatbot interactions
- **GET /health**: Health check endpoint
- **CORS enabled**: Allows frontend to communicate with the API
- **LangGraph integration**: Uses the custom langgraph workflow for RAG

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

### From the api directory:

```bash
cd backend/api
python app.py
```

### From the project root:

```bash
python backend/api/app.py
```

The API will start on `http://localhost:8000`

## API Endpoints

### POST /chat

Receives a user message and returns a bot response using the LangGraph workflow.

**Request:**
```json
{
  "message": "What is LangChain?"
}
```

**Response:**
```json
{
  "response": "LangChain is a framework for developing applications powered by language models...",
  "status": "success"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "response": "User-friendly error message"
}
```

### GET /health

Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Langchain chatbot API is running"
}
```

## Integration with Frontend

The API is designed to work with the Angular frontend located in the `frontend/` directory. The frontend makes POST requests to `http://localhost:8000/chat` with user messages.

## Environment Variables

Make sure you have a `.env` file in the backend directory with the following variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE`: OpenAI API base URL
- `EMBEDDING_MODEL`: Model name for embeddings
- `GENERATION_MODEL`: Model name for text generation

## Architecture

The API acts as a bridge between:
1. **Frontend** (Angular app) → sends user messages
2. **API** (Flask) → processes requests
3. **LangGraph** → executes RAG workflow (retrieve + generate)
4. **Qdrant** → vector database for document retrieval

