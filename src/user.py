from flask import Blueprint, request, jsonify
import mysql.connector
from database.connection import get_db





user_bp = Blueprint('user', __name__)
@user_bp.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # Required fields based on the SQL table structure
    required_fields = ["tc_id", "birth_date", "name", "surname", "email", "blood_type",]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    tc_id = data["tc_id"]
    location = data.get("location")
    birth_date = data["birth_date"]
    name = data["name"]
    surname = data["surname"]
    email = data["email"]
    blood_type = data.get("blood_type")
    last_donation_date = data.get("last_donation_date")
    is_eligible = data.get("is_eligible", True)

    try:
        connection = get_db()
        cursor = connection.cursor()

        # SQL Query to insert a new user
        insert_query = """
            INSERT INTO User (TC_ID, Location, Birth_Date, Name, Surname, Email, Blood_Type, Last_Donation_Date, Is_Eligible)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (tc_id, location, birth_date, name, surname, email, blood_type, last_donation_date, is_eligible)

        cursor.execute(insert_query, values)
        connection.commit()

        return jsonify({"message": "User created successfully"}), 200

    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500

    finally:
        cursor.close()



@user_bp.route("/get_user/<int:tc>", methods=["GET"])
def get_user(tc):
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # SQL Query to get a user by TC_ID
        select_query = """
            SELECT * FROM User WHERE TC_ID = %s
        """
        cursor.execute(select_query, (tc,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify(user), 200

    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500

    finally:
        cursor.close()

@user_bp.route("/users", methods=["GET"])
def get_users():
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # SQL Query to get all users
        select_query = """
            SELECT COUNT(*) as total FROM User
        """
        cursor.execute(select_query)
        user_count = cursor.fetchone()['total']

        return jsonify({
                "total" : user_count
            }), 200

    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500