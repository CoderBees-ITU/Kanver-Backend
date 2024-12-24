from datetime import datetime
from flask import Blueprint, jsonify, request
import mysql.connector
from database.connection import get_db

request_bp = Blueprint('request', __name__)

@request_bp.route("/request", methods=["GET", "POST"])
def handle_request():
    if request.method == "GET":
        return get_requests()
    elif request.method == "POST":
        return create_request()

@request_bp.route("/request/filter", methods=["POST"])
def get_requests():
    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400

    query = "SELECT * FROM Requests WHERE 1=1"
    filters = []

    if "requested_tc_id" in data:
        query += " AND Requested_TC_ID = %s"
        filters.append(data["requested_tc_id"])
    if "patient_tc_id" in data:
        query += " AND Patient_TC_ID = %s"
        filters.append(data["patient_tc_id"])
    if "blood_type" in data:
        query += " AND Blood_Type = %s"
        filters.append(data["blood_type"].strip())
    if "age" in data:
        query += " AND Age = %s"
        filters.append(data["age"])
    if "gender" in data:
        query += " AND Gender = %s"
        filters.append(data["gender"])
    if "location" in data:
        query += " AND Location = %s"
        filters.append(data["location"])
    if "status" in data:
        query += " AND Status = %s"
        filters.append(data["status"])

    query += " ORDER BY Create_Time DESC"

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, filters)
        results = cursor.fetchall()

        if not results:
            return jsonify({"error": "NotFound", "message": "No requests found."}), 404

        return jsonify(results), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()

def create_request():
    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400

    required_fields = ["requested_tc_id", "patient_tc_id", "blood_type", "age", "gender", "location", "status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "InvalidInput", "message": f"The '{field}' field is required."}), 400

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
            return jsonify({"error": "InvalidInput", "message": "TC_ID of requester is not found in the database."}), 400

        city_name, district_name = location.split(',', 1)
        city_name = city_name.strip()
        district_name = district_name.strip()

        check_location_query = "SELECT COUNT(*) FROM Locations WHERE City_Name = %s AND District_Name = %s"
        cursor.execute(check_location_query, (city_name, district_name + "\r"))
        location_result = cursor.fetchone()

        if location_result[0] == 0:
            return jsonify({"error": "InvalidInput", "message": "Invalid location."}), 400

        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-']
        if blood_type not in valid_blood_types:
            return jsonify({"error": "InvalidInput", "message": "Invalid blood type provided."}), 400

        check_spam_query = "SELECT COUNT(*) FROM Requests WHERE Requested_TC_ID = %s AND Patient_TC_ID = %s AND Status = %s"
        cursor.execute(check_spam_query, (requested_tc_id, patient_tc_id, status))
        spam_result = cursor.fetchone()

        if spam_result[0] > 0:
            return jsonify({"error": "InvalidInput", "message": "Duplicate request detected. Spam prevention triggered."}), 400

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
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
