from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path to import langgraph_comp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_comp.graph import langchain_graph

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that receives user messages and returns bot responses.
    Expects JSON: { "message": "user message" }
    Returns JSON: { "response": "bot response" }
    """
    try:
        # Get the user message from request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'No message provided',
                'response': 'Please provide a message.'
            }), 400
        
        user_message = data['message']
        
        if not user_message.strip():
            return jsonify({
                'error': 'Empty message',
                'response': 'Please provide a non-empty message.'
            }), 400
        
        print(f"Received message: {user_message}")
        
        # Call the langgraph graph with the user's query
        result = langchain_graph.invoke({"query": user_message})
        
        # Extract the answer from the result
        bot_response = result.get("answer", "I'm sorry, I couldn't generate a response.")
        
        print(f"Generated response: {bot_response}")
        
        # Return the response
        return jsonify({
            'response': bot_response,
            'status': 'success'
        }), 200
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'response': 'Sorry, I encountered an error processing your request.'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint to verify the API is running.
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Langchain chatbot API is running'
    }), 200

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("API will be available at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)

