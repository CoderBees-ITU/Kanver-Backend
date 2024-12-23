from datetime import datetime
from flask import Blueprint, jsonify, request
import mysql.connector
from database.connection import get_db

request_bp = Blueprint('request', __name__)
@request_bp.route("/create_request", methods=["POST"])
def create_request():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # Required fields based on the SQL table structure
    required_fields = ["requested_tc_id", "patient_tc_id", "blood_type", "age", "gender", "location", "status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    # Extract data with default values for optional fields
    requested_tc_id = data["requested_tc_id"]
    patient_tc_id = data.get("patient_tc_id")
    blood_type = data["blood_type"]
    age = data.get("age")
    gender = data.get("gender")
    note = data.get("note")
    location = data["location"]
    coordinates = data.get("coordinates")
    status = data["status"]
    create_time = datetime.now()

    try:
        connection = get_db()
        cursor = connection.cursor()
        
        check_user_query = "SELECT COUNT(*) FROM User WHERE TC_ID = %s"
        cursor.execute(check_user_query, (requested_tc_id,))
        result = cursor.fetchone()

        if result[0] == 0:
            return jsonify({"message": "TC_ID of Requester is not found in the database"}), 400
        
        #location comes in the format "city, district".
        city_name, district_name = location.split(',', 1)
        city_name = city_name.strip()
        district_name = district_name.strip()
        
        check_location_query = """
            SELECT COUNT(*) FROM Locations WHERE City_Name = %s AND District_Name = %s
        """
        cursor.execute(check_location_query, (city_name, district_name+"\r"))
        location_result = cursor.fetchone()
        
        if location_result[0] == 0:
            return jsonify({"message": "Invalid location."}), 400
        
        check_spam_query = """
            SELECT COUNT(*) FROM Requests WHERE Requested_TC_ID = %s AND Patient_TC_ID = %s AND Status = %s
        """
        cursor.execute(check_spam_query, (requested_tc_id, patient_tc_id, status))
        spam_result = cursor.fetchone()
        
        if spam_result[0] > 0:
            return jsonify({"message": "Spam is prevented"}), 400

        # SQL Query to insert a new request
        insert_query = """
            INSERT INTO Requests (
                Requested_TC_ID, Patient_TC_ID, Blood_Type, Age, Gender, Note,
                Location, Coordinates, Status, Create_Time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            requested_tc_id, patient_tc_id, blood_type, age, gender, note,
            location, coordinates, status, create_time
        )

        cursor.execute(insert_query, values)
        connection.commit()

        return jsonify({"message": "Request created successfully", "request_id": cursor.lastrowid}), 200

    except mysql.connector.Error as err:
        return jsonify({"message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
