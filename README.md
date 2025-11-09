## LangChain Documentation Chatbot

A lightweight documentation-focused chatbot built with LangChain, LangGraph, a Flask-based backend, and a Vite-powered AngularJS frontend.

This repository contains a RAG (Retrieval-Augmented Generation) workflow that uses Qdrant for vector storage and OpenAI models for embeddings and generation.

## What's changed

- Clarified setup steps and requirements (use `backend/pyproject.toml` for Python deps).
- Documented the available convenience scripts (`build.sh`, `run.sh`) and recommended usage.
- Fixed a few references (frontend uses AngularJS + Vite, not modern Angular CLI).

## Quick start (recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd Langchain-chatbot
```

2. Run the setup helper (creates venv, installs Python and Node deps):

```bash
chmod +x build.sh
./build.sh setup
```

3. Start both services (background) with the helper:

```bash
./build.sh start
```

Logs are written to `./logs` and PIDs are stored in `./.service_pids`.

Use `./build.sh stop` to stop the services started by `start`.

## Manual setup

Prerequisites:

- Python 3.12+
- Node.js 18+ and npm (or pnpm)
- OpenAI API access (or another compatible model endpoint)
- Qdrant instance (cloud or local) if you want vector search

Backend (Python)

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install the backend package (uses the project `pyproject.toml` in `backend/`):

```bash
pip install -e ./backend
```

3. Create a `.env` file inside `backend/` with your secrets (example):

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
GENERATION_MODEL=gpt-3.5-turbo
QDRANT_URL=https://your-qdrant-host
QDRANT_API_KEY=your_qdrant_api_key
```

4. Run the backend API (from project root):

```bash
python backend/api/app.py
```

By default the API listens on http://localhost:8000 (check `backend/api/app.py` for exact settings).

Frontend (AngularJS + Vite)

1. Install dependencies and run the dev server:

```bash
cd frontend
npm install
npm run dev
```

2. Open the app in your browser (Vite default):

http://localhost:5173

## Project layout (high level)

```
├── backend/
│   ├── api/                 # Flask REST API (entry: backend/api/app.py)
│   ├── data_insertion/      # Scripts to prepare and insert data into Qdrant
│   └── langgraph_comp/      # LangGraph workflow definitions
├── frontend/                # AngularJS + Vite frontend (src/, index.html)
├── build.sh                 # Helper to setup and run services
├── run.sh                   # Convenience script to run backend+frontend (legacy)
└── logs/                    # Log files created by the helper scripts
```

## Data insertion

Data insertion utilities live under `backend/data_insertion`. Use `insertion.py` and `db_operations.py` to index documents into Qdrant. The `backend/data_insertion/data/` folder contains example text and PDF sources organized by topic.

## API endpoints

- POST /chat — send a user message and receive a response (RAG flow)
- GET /health — health check

See `backend/api/README.md` for details on request/response shapes and examples.

## Contributing

Contributions are welcome. A minimal workflow:

1. Fork the repo
2. Create a feature branch
3. Add tests (where applicable)
4. Open a pull request

Please follow existing code style and include a short description of your changes.

## License

MIT

## Notes and next steps

- If you'd like, I can: update `backend/api/README.md` with concrete cURL examples, add a small health-check test, or create a short `DEVELOPMENT.md` with common debugging steps.
