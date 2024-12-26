from functools import wraps
from flask import request, jsonify, g
from firebase_admin import auth

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({"error": "Unauthorized", "message": "Token is missing."}), 401

        try:
            # Remove 'Bearer ' prefix if present
            token = token.replace('Bearer ', '')

            # Verify the Firebase token
            decoded_token = auth.verify_id_token(token)
            g.user = decoded_token  # Store user details in Flask's global context
        except Exception as e:
            return jsonify({"error": "Unauthorized", "message": "Invalid token. {}".format(e)}), 401

        return f(*args, **kwargs)
    return decorated_function
