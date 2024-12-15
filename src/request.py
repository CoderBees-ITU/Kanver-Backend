from datetime import datetime
from flask import jsonify, request
import mysql.connector
from database.connection import get_db
from flask import Blueprint


request_bp = Blueprint('request', __name__)
@request_bp.route("/create_request", methods=["POST"])
def create_request():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    # Required fields based on the SQL table structure
    required_fields = ["requested_tc_id", "blood_type", "location", "status"]
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
