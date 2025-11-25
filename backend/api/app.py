from flask import Flask, request, jsonify, make_response, session, Response, stream_with_context
from flask_cors import CORS
import sys
import os
import uuid
import json
from functools import wraps
from flask_security import Security, MongoEngineUserDatastore, login_user, logout_user, auth_required, current_user, hash_password, verify_password
from datetime import datetime
from mongoengine import DoesNotExist

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
from models import init_db, User, ThreadInfo
from db_connect import langgraph_collection

# Initialize MongoDB connection
init_db(app)

# Create User datastore and Security
# Pass None for role_model to disable roles
user_datastore = MongoEngineUserDatastore(None, User, None)
security = Security(app, user_datastore)

CORS(app, supports_credentials=True)

from logging_config import get_logger

logger = get_logger(__name__)
memory = langgraph_collection()

# Helper Functions

def find_and_append_thread(thread_id, user_email):
    try:
        user = User.objects.get(email=user_email)

        # Check if thread exists
        if any(t.thread_id == thread_id for t in user.threads):
            # Thread already exists
            return True

        # Add new thread
        new_thread = ThreadInfo(
            thread_id=thread_id,
            timestamp=datetime.utcnow(),
            headline="New Conversation",
            active=True
        )
        user.threads.append(new_thread)
        user.save()

        logger.info(f"Thread ID {thread_id} appended to user {user_email}.")
        return True

    except DoesNotExist:
        logger.error(f"User {user_email} does not exist.")
        return False

def chatHistory(user_email, thread_id):
    # Make sure the thread exists in our new structure
    find_and_append_thread(thread_id, user_email)

    config = {"configurable" : {"thread_id" : thread_id , "user_id" : user_email} }

    try:
        checkpoint = memory.get(config)
        if not checkpoint:
             return {"question": [], "generation": [], "documents": [], "timestamp": None}

        logger.info(f"Checkpoint content: {checkpoint}")
        messages = checkpoint.get("channel_values", {}).get("messages", [])
        timestamp = checkpoint.get("ts", None)
        question = []
        answer = []
        documents = []

        # Assuming messages are [Human, AI, Human, AI...]
        # We iterate by 2 to get pairs
        for i in range(0, len(messages)-1, 2):
            if i+1 < len(messages):
                question.append(messages[i].content)
                
                # Get the bot response content
                ai_msg = messages[i+1]
                # Check if content is a list or string
                if isinstance(ai_msg.content, list) and len(ai_msg.content) >= 2:
                     answer.append(ai_msg.content[0])
                else:
                     answer.append(ai_msg.content)

        history = {
            "question": question,
            "generation": answer, 
            "timestamp": timestamp
        }
        return history
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return {"question": [], "generation": [], "documents": [], "timestamp": None}


# Endpoints

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
        
        logger.info("User logged in: %s", user.email if 'user' in locals() else 'Unknown')
        
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

@app.route('/thread_history', methods=['POST'])
@auth_required()
def handle_history():
    """Handle POST request to process a query using graph.invoke()."""
    try:
        data = request.get_json()
        thread_id = data.get('thread_id', '')
        user_email = current_user.email
        
        if not thread_id:
            return jsonify({"error": "Please provide a 'thread_id' in JSON format"}), 400

        # Run the graph using invoke()
        result = chatHistory(user_email, thread_id)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving thread history: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/user_threads', methods=['GET'])
@auth_required()
def get_user_threads():
    try:
        user = User.objects.get(id=current_user.id)
        threads = []
        for t in user.threads:
            if t.active:
                threads.append({
                    'thread_id': t.thread_id,
                    'headline': t.headline,
                    'timestamp': t.timestamp
                })
        return jsonify({'userId': str(user.id), 'threads': threads}), 200
    except Exception as e:
        logger.error(f"Error retrieving user threads: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete_thread', methods=['POST'])
@auth_required()
def delete_thread():
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        
        if not thread_id:
            return jsonify({'success': False, 'message': 'Thread ID required'}), 400
            
        user = User.objects.get(id=current_user.id)
        
        # Soft delete
        for t in user.threads:
            if t.thread_id == thread_id:
                t.active = False
                user.save()
                return jsonify({'success': True, 'message': 'Thread deleted'}), 200
                
        return jsonify({'success': False, 'message': 'Thread not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting thread: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/query', methods=['POST'])
@auth_required()
def query():
    user_id = current_user.id
    data = request.get_json()
    question = data.get('question')
    thread_id = data.get('thread_id')

    if not question or not thread_id:
        return jsonify({"error": "Missing question or thread_id"}), 400

    # Ensure thread exists/is linked to user
    find_and_append_thread(thread_id, current_user.email)

    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Invoke the graph
        final_state = langchain_graph.invoke(
            {"query": question},
            config=config
        )

        # Check for headline and update if necessary
        if 'headline' in final_state:
            new_headline = final_state['headline']
            # Ensure headline fits in 255 chars
            if new_headline and len(new_headline) > 255:
                logger.warning(f"Headline too long ({len(new_headline)} chars), truncating: {new_headline[:50]}...")
                new_headline = new_headline[:252] + "..."
            # Reload user to ensure we have the latest state and can save
            user = User.objects.get(id=current_user.id)
            thread_updated = False
            for t in user.threads:
                if t.thread_id == thread_id:
                    # Only update if it's currently "New Conversation"
                    if t.headline == "New Conversation":
                         t.headline = new_headline
                         thread_updated = True
                    break
            
            if thread_updated:
                user.save()
                logger.info(f"Updated headline for thread {thread_id} to: {new_headline}")
        
        # Remove messages from final_state as they are not serializable and not needed by frontend
        if 'messages' in final_state:
            del final_state['messages']

        return jsonify(final_state)

    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500


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
    # Configure logging for standalone run
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Flask API server...")
    logger.info("API will be available at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)

