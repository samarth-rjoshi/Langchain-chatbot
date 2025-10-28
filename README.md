# LangChain Documentation Chatbot

A sophisticated chatbot application built using LangChain, LangGraph, Flask, and Angular that provides intelligent responses to queries about LangChain documentation. The chatbot uses advanced language models, vector stores, and a custom LangGraph workflow to deliver accurate and context-aware answers.

## Features

- 🤖 Interactive chatbot interface using Angular
- 🔄 LangGraph-powered RAG (Retrieval-Augmented Generation) workflow
- 🌐 Flask REST API backend
- 📚 Comprehensive LangChain documentation coverage
- 🔍 Vector search using Qdrant for efficient document retrieval
- 🎯 Context-aware responses using OpenAI models
- 💾 Persistent chat history
- 🎨 Beautiful and responsive UI

## Project Structure

```
├── backend/
│   ├── api/                    # Flask REST API
│   │   ├── app.py             # Main Flask application
│   │   ├── run.sh             # Unix startup script
│   │   ├── run.bat            # Windows startup script
│   │   └── README.md          # API documentation
│   ├── langgraph_comp/        # LangGraph workflow
│   │   └── graph.py           # RAG workflow implementation
│   ├── data_insertion/        # Data processing and insertion
│   │   ├── db_operations.py   # Qdrant database operations
│   │   ├── insertion.py       # Document insertion logic
│   │   └── data/              # Documentation data
│   └── main.py                # Backend entry point
├── frontend/                   # Angular frontend
│   ├── src/
│   │   ├── app.js             # Angular application
│   │   └── style.css          # Styles
│   ├── index.html             # Main HTML file
│   └── package.json           # Frontend dependencies
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- OpenAI API access
- Qdrant cloud account and API keys

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd langchain-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

5. Set up environment variables:
Create a `.env` file in the `backend` directory and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
GENERATION_MODEL=gpt-3.5-turbo
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## Running the Application

### Backend (Flask API)

1. Start the Flask API server:

**On Unix/Linux/Mac:**
```bash
cd backend/api
./run.sh
```

**On Windows:**
```bash
cd backend\api
run.bat
```

**Or directly with Python:**
```bash
python backend/api/app.py
```

The API will be available at `http://localhost:8000`

### Frontend (Angular)

1. In a new terminal, start the frontend development server:
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

2. Open your browser and navigate to `http://localhost:5173` to use the chatbot!

## Features in Detail

### LangGraph Workflow
- Custom RAG workflow with retrieve and generate nodes
- Efficient document retrieval from Qdrant vector store
- Context-aware answer generation using OpenAI models
- Seamless integration with Flask API

### REST API (Flask)
- **POST /chat**: Main endpoint for chatbot interactions
- **GET /health**: Health check endpoint
- CORS-enabled for frontend communication
- Error handling and logging

### Vector Store Integration
- Uses Qdrant as a vector store for efficient document retrieval
- Supports multiple collections for different documentation sources
- Implements semantic search for accurate document matching

### User Interface (Angular)
- Clean and modern design with custom CSS styling
- Real-time chat interface with loading indicators
- Message timestamps
- Responsive design for all screen sizes

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain team for the excellent framework
- Haystack team for their contribution to NLP
- Streamlit team for the amazing web framework
- HuggingFace for providing access to state-of-the-art language models
- Qdrant team for their vector database solution
