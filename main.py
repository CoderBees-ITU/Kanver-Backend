from flask import Flask, jsonify, request, session
from datetime import timedelta
import os
import secrets
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask_cors import CORS
from auth import register

app = Flask(__name__)
CORS(app, support_credentials=True)

# Set a secret key. Ensure this is set securely in production (e.g., through an env var).
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_local_dev')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Firebase Admin SDK setup
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def hello_world():
    return jsonify({"message": "Hello, World!"})

@app.route("/register", methods=["POST"])
def registerC():
    return register()


@app.route("/check-auth", methods=["POST"])
def check_auth():
    data = request.get_json() or {}
    client_session_key = data.get('session_key', None)

    if 'logged_in' in session and session['logged_in']:
        # Verify the session key matches what we have on server
        if client_session_key and session.get('session_key') == client_session_key:
            return jsonify({"message": "User is authenticated", "email": session['email']}), 200
        else:
            return jsonify({"message": "Session key mismatch or not provided"}), 401
    else:
        return jsonify({"message": str(session["logged_in"])}), 401
        return jsonify({"message": "Not authenticated"}), 401

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
