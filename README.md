# 🤖 LangChain Documentation Chatbot

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Frontend](https://img.shields.io/badge/frontend-AngularJS%20%2B%20Vite-red)
![Status](https://img.shields.io/badge/status-active-success.svg)

A powerful, production-ready RAG (Retrieval-Augmented Generation) chatbot designed to answer questions from documentation. Built with a modern Python backend using **LangChain** and **LangGraph**, and a responsive **AngularJS** frontend powered by **Vite**.

## ✨ Features

- **📚 RAG Architecture**: Retrieval-Augmented Generation for accurate, context-aware answers.
- **🧠 LangGraph Workflows**: State-of-the-art agentic workflows for managing conversation state.
- **⚡ Fast Vector Search**: Utilizes **Qdrant** for high-performance vector similarity search.
- **🔐 Secure Authentication**: Session-based authentication with **Flask-Security** and **MongoDB**.
- **💬 Persistent Chat**: Chat history and thread management stored in MongoDB.
- **🚀 Modern Stack**:
  - **Backend**: Flask, LangChain, LangGraph, OpenAI, Qdrant, MongoEngine.
  - **Frontend**: AngularJS (1.x), Vite, TailwindCSS (optional/custom).


## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**
- **Node.js 18+** & **npm**
- **MongoDB** (Local or Atlas)
- **Qdrant** (Local Docker container or Cloud)
- **OpenAI API Key**

## 🚀 Quick Start

The easiest way to get up and running is using the included helper script.

### 1. Clone the repository
```bash
git clone <repository-url>
cd Langchain-chatbot
```

### 2. Setup Environment
Run the setup command to create the virtual environment and install dependencies for both backend and frontend.
```bash
chmod +x build.sh
./build.sh setup
```

### 3. Configure Secrets
Create a `.env` file in the `backend/` directory:
```bash
cp backend/.env.example backend/.env # if example exists, else create manually
```
**Required `.env` variables:**
```env
QDRANT_URL=
QDRANT_API_KEY=
EMBEDDING_MODEL=
OPENAI_API_KEY=
OPENAI_API_BASE=
COLLECTION_NAME=
GENERATION_MODEL=
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=

MONGO_URI=

```

### 4. Start the Application
Start both the backend and frontend services in the background.
```bash
./build.sh start
```
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Logs**: Check `./logs/` directory.

To stop the services:
```bash
./build.sh stop
```

## ⚙️ Manual Setup

If you prefer to run services manually or for debugging:

### Backend
```bash
cd backend
# Create virtual env
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run the server
python api/app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📂 Project Structure

```
Langchain-chatbot/
├── backend/
│   ├── api/                 # Flask API endpoints & app entry point
│   ├── data_insertion/      # Scripts for ingesting docs into Qdrant
│   ├── langgraph_comp/      # LangGraph agent definitions & logic
│   ├── models.py            # Database models (User, Chat)
│   └── pyproject.toml       # Python dependencies
|   |__ evaluators           # LLM as a judge evaluation
├── frontend/
│   ├── src/                 # AngularJS components & logic
│   ├── index.html           # Entry HTML
│   └── package.json         # Frontend dependencies
├── build.sh                 # Unified setup & control script
└── run.sh                   # Legacy run script
```

## 🧠 Data Ingestion

To populate the chatbot with knowledge, use the scripts in `backend/data_insertion/`.

1. Place your PDF or text files in `backend/data_insertion/data/`.
2. Run the insertion script (ensure your `.env` is set):
   ```bash
   cd backend
   python data_insertion/insertion.py
   ```
## 🧪 Running LangSmith Evaluations

We have local evaluation workflows set up using **LangSmith's LLM-as-a-judge**. This evaluates the RAG accuracy, relevance, and hallucination footprint against your documents.

### How to Evaluate
1. Make sure your local endpoint (e.g., LM studio) and your Qdrant instance are reachable.
2. Run the evaluator module:
   ```bash
   python -m evaluators.evaluate_rag
   ```

