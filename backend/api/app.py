from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
import sys
import os
import uuid
from functools import wraps
from flask_security import Security, MongoEngineUserDatastore, login_user, logout_user, auth_required, current_user, hash_password, verify_password

# Add parent directory to path to import langgraph_comp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_comp.graph import langchain_graph
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-' + str(uuid.uuid4()))
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT', 'dev-salt-change-in-production')
app.config['MONGODB_HOST'] = os.getenv("MONGO_URI")

# Flask-Security Config
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_USERNAME_ENABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_URL_PREFIX'] = '/security'

# JSON API mode (useful for frontends / mobile / SPA)
app.config['SECURITY_JSON_API'] = True
app.config['WTF_CSRF_ENABLED'] = False

# Use centralized models module
from models import init_db, User

# Initialize MongoDB connection
init_db(app)

# Create User datastore and Security
# Pass None for role_model to disable roles
user_datastore = MongoEngineUserDatastore(None, User, None)
security = Security(app, user_datastore)

CORS(app, supports_credentials=True)

from logging_config import get_logger

logger = get_logger(__name__)

# Custom login_required removed in favor of Flask-Security's auth_required or login_required

@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint that authenticates user and sets session.
    Expects JSON: { "username": "username", "password": "password" }
    Returns JSON: { "status": "success", "message": "Login successful" }
    """
    try:
        data = request.get_json()
        
        if not data or ('username' not in data and 'email' not in data) or 'password' not in data:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Please provide username/email and password.'
            }), 400
        
        # Support both username and email login
        identifier = data.get('username') or data.get('email')
        password = data['password']
        
        user = user_datastore.find_user(email=identifier) or user_datastore.find_user(username=identifier)

        if not user or not verify_password(password, user.password):
             return jsonify({
                'error': 'Invalid credentials',
                'message': 'Invalid username or password.'
            }), 401

        login_user(user)
        
        logger.info("User logged in: %s", user.email)
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'username': user.username or user.email
        }), 200
        
    except Exception as e:
        logger.exception("Error in login endpoint: %s", str(e))
        return jsonify({
            'error': str(e),
            'message': 'Sorry, I encountered an error processing your login request.'
        }), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not email or not password:
             return jsonify({'message': 'Email and password are required'}), 400

        if user_datastore.find_user(email=email):
            return jsonify({'message': 'User already exists'}), 400
            
        user_datastore.create_user(email=email, username=username, password=hash_password(password))
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        logger.exception("Error in register endpoint: %s", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """
    Logout endpoint that clears session.
    Returns JSON: { "status": "success", "message": "Logged out successfully" }
    """
    try:
        logout_user()
        
        logger.info("User logged out")
        
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
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'username': current_user.username or current_user.email
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200

@app.route('/chat', methods=['POST'])
@auth_required()
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

