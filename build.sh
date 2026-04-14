#!/usr/bin/env bash
# Installer helper for Langchain-chatbot: install backend/frontend dependencies only

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "=== Installing backend dependencies (via uv + pyproject.toml) ==="
cd "$BACKEND_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
  echo "❌ 'uv' not found. Please install it first:"
  echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

# Sync all dependencies from pyproject.toml
uv sync

echo "=== Backend setup complete ==="

echo "=== Installing frontend dependencies ==="
cd "$FRONTEND_DIR"

if [ -f "package.json" ]; then
  npm install
  echo "=== Frontend setup complete ==="
else
  echo "No package.json found in $FRONTEND_DIR — skipping frontend install."
fi

echo "✅ All dependencies installed successfully."
 