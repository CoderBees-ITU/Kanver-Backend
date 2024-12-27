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

    required_fields = ["email", "password", "name", "surname", "tc", "blood_type", "birth_date"]
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
            return jsonify({"message": "User already exists"}), 400

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
                                User_id, TC_ID, City, District, Birth_Date, Name, Surname,
                                 Email, Blood_Type, Last_Donation_Date, Is_Eligible
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
        values = (
            user_record.uid, tc, None, None, birth_date, name, surname,
            email, blood_type, None, True)

        mycursor.execute(insert_query, values)
        mydb.commit()

        # Close the cursor and connection
        mycursor.close()
        mydb.close()

        custom_token = auth.create_custom_token(user_record.uid)

        return jsonify({
            "message": "User created successfully",
            "user_id": user_record.uid,
            "session_key": custom_token.decode('utf-8'),
        }), 200
    except Exception as e:
        # Delete the Firebase user if the database operation fails
        try:
            auth.delete_user(user_record.uid)
        except Exception as cleanup_error:
            return jsonify({
                "message": f"Database and Firebase cleanup failed: {str(e)}, {str(cleanup_error)}"
            }), 500

        return jsonify({"message": f"Database operation failed: {str(e)}"}), 400
    finally:
        # Ensure database resources are closed
        if mycursor:
            mycursor.close()
        if mydb:

            mydb.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    connection = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        id_token = data.get('idToken')
        if not id_token:
            return jsonify({"message": "Missing required field: idToken"}), 400

        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get('email')

        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        check_user_query = "SELECT * FROM User WHERE Email = %s"
        cursor.execute(check_user_query, (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404

        check_ban_query = "SELECT * FROM Banned_Users WHERE TC_ID = %s"
        cursor.execute(check_ban_query, (user['TC_ID'],))
        banned_user = cursor.fetchone()

        if banned_user:
            return jsonify({
                "message": "User is banned",
                "ban_reason": banned_user["Cause"],
                "unban_date": banned_user["Unban_Date"]
            }), 403

        # Return user details
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user['User_id'],
                "name": user['Name'],
                "surname": user['Surname'],
                "email": user['Email'],
                "blood_type": user['Blood_Type'],
                "is_eligible": user['Is_Eligible']
            }
        }), 200

    except auth.InvalidIdTokenError:
        return jsonify({"message": "Invalid ID token"}), 401

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"message": "Internal server error"}), 500

    finally:
        #gpt önerdi neden bilmiyorum
        if cursor:
            cursor.close()
        if connection:
            connection.close()
