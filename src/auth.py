from flask import Blueprint, request, jsonify, session
from firebase_admin import auth, app_check
import mysql.connector
from database.connection import get_db
import secrets
import firebase_admin
import flask
import jwt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    required_fields = ["email", "password", "name", "tc", "blood_type"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    email = data["email"]
    password = data["password"]
    name = data["name"]
    surname = data["surname"]
    tc = data["tc"]
    blood_type = data["blood_type"]
    birth_date = data.get("birth_date")

    try:
        # Connect to MySQL
        mydb = get_db()
        mycursor = mydb.cursor()

        # Check if TC_ID or Email already exists in the database
        check_query = "SELECT * FROM User WHERE TC_ID = %s OR Email = %s"
        mycursor.execute(check_query, (tc, email))
        existing_user = mycursor.fetchone()

        if existing_user:
            # Determine the cause of the conflict
            if existing_user[0] == tc:  # Assuming TC_ID is the first column
                return jsonify({"message": "TC_ID is already registered"}), 400
            if existing_user[1] == email:  # Assuming Email is the second column
                return jsonify({"message": "Email is already registered"}), 400

        # Create a user in Firebase
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=name+" "+surname
        )
    except Exception as e:
        # If Firebase user creation fails, report it
        return jsonify({"message": f"Firebase user creation failed: {str(e)}"}), 400

    try:
        # Connect to MySQL
        mydb = get_db()
        mycursor = mydb.cursor()

        # SQL Query to insert a new request
        insert_query = """
        INSERT INTO User (
                                User_id, TC_ID, Location, Birth_Date, Name, Surname,
                                 Email, Blood_Type, Last_Donation_Date, Is_Eligible
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
        values = (
            user_record.uid, tc, None, birth_date, name, surname,
            email, blood_type, None, True)

        mycursor.execute(insert_query, values)
        mydb.commit()

        # Create a server-side session
        session['user_id'] = user_record.uid
        session['email'] = email
        session['logged_in'] = True

        # Generate a session key to return to the client
        session_key = secrets.token_hex(16)
        session['session_key'] = session_key

        # Close the cursor and connection
        mycursor.close()
        mydb.close()

        return jsonify({
            "message": "User created successfully",
            "session_key": session_key
        }), 200
    except Exception as e:
        # Consider deleting the Firebase user if DB insertion fails
        # auth.delete_user(user_record.uid)
        return jsonify({"message": f"Database operation failed: {str(e)}"}), 400


@auth_bp.route('/check_token', methods=['POST'])
def check_token():
    # Parse JSON data from the request
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # Check if 'session_key' field is present in the data
    session_key = data.get('session_key')
    id = data.get('uid')
    if not session_key or not id:
        return jsonify({"message": "Missing field: session_key"}), 400

    # Retrieve the Firebase App Check token from the headers

    try:
        # Verify the Firebase App Check token
        decoded_token = auth.verify_id_token(session_key)
        uid = decoded_token['uid']
        # Check if the session key matches the one stored in the server-side session
        if uid != id:
            return jsonify({"message": "Token is invalid"}), 401
        # Return a success response
        return jsonify({"message": "Token is valid", "claims": uid}), 200
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
        return jsonify({"message": "Internal server error"}), 500
