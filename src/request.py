from datetime import datetime
from flask import Blueprint, jsonify, request
import mysql.connector
from database.connection import get_db
from src.middleware import auth_required

request_bp = Blueprint('request', __name__)

@request_bp.route("/request", methods=["GET"])
# auth_required will be commented out 
# @auth_required
def get_requests():
    requested_tc_id = request.args.get("requested_tc_id")
    patient_tc_id = request.args.get("patient_tc_id")
    blood_type = request.args.get("blood_type")
    age = request.args.get("age")
    gender = request.args.get("gender")
    city = request.args.get("city")
    district = request.args.get("district")
    hospital = request.args.get("hospital")
    status = request.args.get("status")
    request_id = request.args.get("request_id")

    # Start building the query
    query = "SELECT * FROM Requests WHERE 1=1"
    filters = []

    # Add filters based on available parameters
    if requested_tc_id:
        query += " AND Requested_TC_ID = %s"
        filters.append(requested_tc_id)
    if patient_tc_id:
        query += " AND Patient_TC_ID = %s"
        filters.append(patient_tc_id)
    if blood_type:
        query += " AND Blood_Type = %s"
        filters.append(blood_type.strip())
    if age:
        query += " AND Age = %s"
        filters.append(age)
    if gender:
        query += " AND Gender = %s"
        filters.append(gender)
    if city:
        query += " AND City = %s"
        filters.append(city)
    if district:
        query += " AND District = %s"
        filters.append(district)
    if hospital:
        query += " AND Hospital = %s"
        filters.append(hospital)
    if status:
        query += " AND Status = %s"
        filters.append(status)
    if request_id:
        query += " AND Request_ID = %s"
        filters.append(request_id)

    query += " ORDER BY Create_Time DESC"

    try:
        # Connect to the database
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, filters)
        results = cursor.fetchall()

        # Check if results exist
        if not results:
            return jsonify({"error": "NotFound", "message": "No requests found."}), 404

        # Return the results as JSON
        return jsonify(results), 200

    except mysql.connector.Error as err:
        # Handle database errors
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        # Ensure cursor and connection are closed
        cursor.close()
        connection.close()

@request_bp.route("/request", methods=["POST"])
# @auth_required
def create_request():    
    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400

    required_fields = ["requested_tc_id", "patient_tc_id", "blood_type", "age", "gender", "location", "hospital", "status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "InvalidInput", "message": f"The '{field}' field is required."}), 400

    requested_tc_id = data["requested_tc_id"]
    patient_tc_id = data.get("patient_tc_id")
    blood_type = data["blood_type"]
    age = data.get("age")
    gender = data.get("gender")
    note = data.get("note")
    location = data["location"]              #location is a dictionary
    hospital = data["hospital"]
    coordinates = data.get("coordinates")
    status = data["status"]
    create_time = datetime.now()
    
    city = location.get("city")
    district = location.get("district")
    lat= location.get("lat")
    lng = location.get("lng")

    try:
        connection = get_db()
        cursor = connection.cursor()

        check_user_query = "SELECT COUNT(*) FROM User WHERE TC_ID = %s"
        cursor.execute(check_user_query, (requested_tc_id,))
        result = cursor.fetchone()

        if result[0] == 0:
            return jsonify({"error": "InvalidInput", "message": "TC_ID of requester is not found in the database."}), 400

        check_location_query = "SELECT COUNT(*) FROM Locations WHERE City_Name = %s AND District_Name = %s"
        cursor.execute(check_location_query, (city, district + "\r"))
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
                Lat, Lng, City, District, Hospital, Status, Create_Time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            requested_tc_id, patient_tc_id, blood_type, age, gender, note,
            lat, lng, city, district, hospital, status, create_time
        )

        cursor.execute(insert_query, values)
        connection.commit()

        return jsonify({"message": "Request created successfully", "request_id": cursor.lastrowid}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
