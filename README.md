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
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
GENERATION_MODEL=gpt-3.5-turbo
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY= # Leave empty if local without auth
MONGO_URI=mongodb://localhost:27017/langchain_chat
SECRET_KEY=super-secret-key
SECURITY_PASSWORD_SALT=super-secret-salt
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

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
