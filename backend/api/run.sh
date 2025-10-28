#!/bin/bash

# Script to run the Langchain Chatbot API

echo "Starting Langchain Chatbot API..."
echo "=================================="
echo ""

# Check if we're in the api directory
if [ -f "app.py" ]; then
    python app.py
else
    # If not, navigate to the api directory
    cd "$(dirname "$0")" || exit
    python app.py
fi

