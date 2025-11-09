#!/usr/bin/env bash
# Top-level run script to start backend and frontend for local development

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
BACKEND_DIR="$ROOT_DIR/backend"
BACKEND_API_DIR="$BACKEND_DIR/api"
FRONTEND_DIR="$ROOT_DIR/frontend"

mkdir -p "$LOG_DIR"

echo "🚀 Starting Langchain Chatbot (backend + frontend)"
echo "📂 Logs: $LOG_DIR"
echo ""

# --- Helper: check command availability ---
check_command() {
  if ! command -v "$1" &> /dev/null; then
    echo "❌ Error: '$1' not found. Please install it."
    exit 1
  fi
}

check_command uv
check_command npm

PIDS=()

# --- Backend ---
start_backend() {
  echo "=== Starting backend ==="
  cd "$BACKEND_API_DIR"

  # Activate venv if exists
  if [ -d "../.venv" ]; then
    echo "Activating backend virtual environment..."
    # shellcheck source=/dev/null
    source ../.venv/bin/activate
  else
    echo "No .venv found in backend — creating it with uv..."
    cd ..
    uv sync
    cd api
    source ../.venv/bin/activate
  fi

  echo "Running Flask API via uv..."
  uv run python app.py > "$LOG_DIR/backend.log" 2>&1 &
  BACKEND_PID=$!
  PIDS+=("$BACKEND_PID")
  echo "✅ Backend started (PID: $BACKEND_PID)"
}

# --- Frontend ---
start_frontend() {
  echo "=== Starting frontend (Vite) ==="
  cd "$FRONTEND_DIR"

  if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
  fi

  npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
  FRONTEND_PID=$!
  PIDS+=("$FRONTEND_PID")
  echo "✅ Frontend started (PID: $FRONTEND_PID)"
}

# --- Graceful shutdown ---
cleanup() {
  echo ""
  echo "🧹 Stopping all processes..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  echo "✅ All processes stopped."
  exit 0
}

trap cleanup SIGINT SIGTERM

# --- Start both ---
start_backend
start_frontend

echo ""
echo "🌐 Both services are running!"
echo "👉 Tail logs with: tail -f $LOG_DIR/*.log"
echo "👉 Press Ctrl+C to stop."

wait
