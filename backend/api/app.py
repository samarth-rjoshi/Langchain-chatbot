from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
import sys
import os
import uuid
from functools import wraps

# Add parent directory to path to import langgraph_comp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_comp.graph import langchain_graph
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-' + str(uuid.uuid4()))
CORS(app, supports_credentials=True)

from logging_config import get_logger

logger = get_logger(__name__)

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'error': 'Authentication required',
                'response': 'Please log in to access this resource.'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint that authenticates user and sets session.
    Expects JSON: { "username": "username", "password": "password" }
    Returns JSON: { "status": "success", "message": "Login successful" }
    """
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Please provide both username and password.'
            }), 400
        
        username = data['username']
        password = data['password']
        
        # Simple authentication (in production, use proper password hashing and database)
        # For demo purposes, accept any non-empty username/password
        if not username.strip() or not password.strip():
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Username and password cannot be empty.'
            }), 401
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store user info in session
        session['user_id'] = session_id
        session['username'] = username
        session['logged_in'] = True
        
        logger.info("User logged in: %s (session_id: %s)", username, session_id)
        
        # Create response with JSON data
        response = make_response(jsonify({
            'status': 'success',
            'message': 'Login successful',
            'username': username
        }), 200)
        
        
        return response
        
    except Exception as e:
        logger.exception("Error in login endpoint: %s", str(e))
        return jsonify({
            'error': str(e),
            'message': 'Sorry, I encountered an error processing your login request.'
        }), 500

@app.route('/logout', methods=['POST'])
def logout():
    """
    Logout endpoint that clears session.
    Returns JSON: { "status": "success", "message": "Logged out successfully" }
    """
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        
        logger.info("User logged out: %s", username)
        
        response = make_response(jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 200)
        
        
        return response
        
    except Exception as e:
        logger.exception("Error in logout endpoint: %s", str(e))
        return jsonify({
            'error': str(e),
            'message': 'Sorry, I encountered an error processing your logout request.'
        }), 500

@app.route('/check-auth', methods=['GET'])
def check_auth():
    """
    Check if user is authenticated.
    Returns JSON: { "authenticated": true/false, "username": "username" }
    """
    if 'logged_in' in session and session['logged_in']:
        return jsonify({
            'authenticated': True,
            'username': session.get('username', 'Unknown')
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200

@app.route('/chat', methods=['POST'])
@login_required
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
        
        logger.info("Received message: %s", user_message)
        
        # Call the langgraph graph with the user's query
        result = langchain_graph.invoke({"query": user_message})
        
        # Extract the answer from the result
        bot_response = result.get("answer", "I'm sorry, I couldn't generate a response.")
        
        logger.info("Generated response: %s", bot_response)
        
        # Return the response (session is already set during login)
        return jsonify({
            'response': bot_response,
            'status': 'success'
        }), 200
        
    except Exception as e:
        logger.exception("Error in chat endpoint: %s", str(e))
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


# Frontend log endpoint removed — frontend logs are not required per project configuration.

if __name__ == '__main__':
    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Flask API server...")
    logger.info("API will be available at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)

