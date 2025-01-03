from datetime import datetime
from flask import Blueprint, jsonify, request
import mysql.connector
from database.connection import get_db
from src.middleware import auth_required
from src.notification import create_notification_logic

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
    user_id = request.headers.get("Authorization")

    # Start building the query
    query = """
        WITH OnTheWayCount AS (
            SELECT Request_ID, COUNT(*) AS On_The_Way_Count
            FROM On_The_Way 
            GROUP BY Request_ID
        )
        SELECT R.*, 
               COALESCE(OTW.On_The_Way_Count, 0) AS On_The_Way_Count
        FROM Requests R
        LEFT JOIN OnTheWayCount OTW ON R.Request_ID = OTW.Request_ID
        WHERE R.Request_ID NOT IN (
            SELECT Request_ID 
            FROM On_The_Way 
            WHERE Donor_TC_ID = %s
        )
    """
    filters = [None]

    # Add filters based on available parameters
    if requested_tc_id:
        query += " AND R.Requested_TC_ID = %s"
        filters.append(requested_tc_id)
    if patient_tc_id:
        query += " AND R.Patient_TC_ID = %s"
        filters.append(patient_tc_id)
    if blood_type:
        query += " AND R.Blood_Type = %s"
        filters.append(blood_type.strip())
    if age:
        query += " AND R.Age = %s"
        filters.append(age)
    if gender:
        query += " AND R.Gender = %s"
        filters.append(gender)
    if city:
        query += " AND R.City = %s"
        filters.append(city)
    if district:
        query += " AND R.District = %s"
        filters.append(district)
    if hospital:
        query += " AND R.Hospital = %s"
        filters.append(hospital)
    if status:
        query += " AND R.Status = %s"
        filters.append(status)
    if request_id:
        query += " AND R.Request_ID = %s"
        filters.append(request_id)
        
    query += " GROUP BY R.Request_ID ORDER BY R.Create_Time DESC"

    try:
        # Connect to the database
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400

        donor_tc_id = user["TC_ID"]
        filters[0] = donor_tc_id
        
        cursor.execute(query, filters)
        results = cursor.fetchall()

        for row in results:
            row['Create_Time'] = row['Create_Time'].strftime('%Y-%m-%d %H:%M:%S')

        # Return the results as JSON
        return jsonify(results), 200

    except mysql.connector.Error as err:
        # Handle database errors
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        # Ensure cursor and connection are closed
        cursor.close()
        connection.close()

        
@request_bp.route("/request/my_requests", methods=["GET"])
# auth_required will be commented out 
# @auth_required
def get_my_requests():
    patient_tc_id = request.args.get("patient_tc_id")
    blood_type = request.args.get("blood_type")
    age = request.args.get("age")
    gender = request.args.get("gender")
    city = request.args.get("city")
    district = request.args.get("district")
    hospital = request.args.get("hospital")
    status = request.args.get("status")
    request_id = request.args.get("request_id")
    
    user_id = request.headers.get("Authorization")
    
    filters = [None]
    
    # Use CTE to calculate On_The_Way_Count
    select_query = """
        WITH OnTheWayCount AS (
            SELECT Request_ID, COUNT(*) AS On_The_Way_Count
            FROM On_The_Way
            GROUP BY Request_ID
        )
        SELECT R.*, 
               COALESCE(OTW.On_The_Way_Count, 0) AS On_The_Way_Count
        FROM Requests R
        LEFT JOIN OnTheWayCount OTW ON R.Request_ID = OTW.Request_ID
        WHERE R.Requested_TC_ID = %s
    """
    
    if patient_tc_id:
        select_query += " AND R.Patient_TC_ID = %s"
        filters.append(patient_tc_id)
    if blood_type:
        select_query += " AND R.Blood_Type = %s"
        filters.append(blood_type.strip())
    if age:
        select_query += " AND R.Age = %s"
        filters.append(age)
    if gender:
        select_query += " AND R.Gender = %s"
        filters.append(gender)
    if city:
        select_query += " AND R.City = %s"
        filters.append(city)
    if district:
        select_query += " AND R.District = %s"
        filters.append(district)
    if hospital:
        select_query += " AND R.Hospital = %s"
        filters.append(hospital)
    if status:
        select_query += " AND R.Status = %s"
        filters.append(status)
    if request_id:
        select_query += " AND R.Request_ID = %s"
        filters.append(request_id)
        
    select_query += " ORDER BY R.Create_Time DESC"
    
    try:
        # Connect to the database
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        # Check if user exists
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400

        user_tc_id = user["TC_ID"]
        filters[0] = user_tc_id

        # Execute the main query
        cursor.execute(select_query, filters)
        results = cursor.fetchall()
        
        # Format the Create_Time column
        for row in results:
            row['Create_Time'] = row['Create_Time'].strftime('%Y-%m-%d %H:%M:%S')

        # Return the results as JSON
        return jsonify(results), 200

    except mysql.connector.Error as err:
        # Handle database errors
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        # Ensure cursor and connection are closed
        cursor.close()
        connection.close()

    
@request_bp.route("/request/personalized", methods=["GET"])
# auth_required will be commented out 
# @auth_required
def get_personalized_requests():
    patient_tc_id = request.args.get("patient_tc_id")
    blood_type = request.args.get("blood_type")
    age = request.args.get("age")
    gender = request.args.get("gender")
    city = request.args.get("city")
    district = request.args.get("district")
    hospital = request.args.get("hospital")
    status = request.args.get("status")
    request_id = request.args.get("request_id")
    
    user_id = request.headers.get("Authorization")
    
    filters = [None, None]

    # Use CTE to calculate On_The_Way_Count
    select_personalized_requests_query = """
        WITH OnTheWayCount AS (
            SELECT Request_ID, COUNT(*) AS On_The_Way_Count
            FROM On_The_Way
            GROUP BY Request_ID
        )
        SELECT R.*, 
               COALESCE(OTW.On_The_Way_Count, 0) AS On_The_Way_Count
        FROM Requests R
        LEFT JOIN OnTheWayCount OTW ON R.Request_ID = OTW.Request_ID
        WHERE R.Status != 'closed'
          AND R.Requested_TC_ID != %s
          AND NOT EXISTS (
              SELECT 1
              FROM On_The_Way O
              WHERE O.Request_ID = R.Request_ID
                AND O.Donor_TC_ID = %s
          )
    """
    
    if patient_tc_id:
        select_personalized_requests_query += " AND R.Patient_TC_ID = %s"
        filters.append(patient_tc_id)
    if blood_type:
        select_personalized_requests_query += " AND R.Blood_Type = %s"
        filters.append(blood_type.strip())
    if age:
        select_personalized_requests_query += " AND R.Age = %s"
        filters.append(age)
    if gender:
        select_personalized_requests_query += " AND R.Gender = %s"
        filters.append(gender)
    if city:
        select_personalized_requests_query += " AND R.City = %s"
        filters.append(city)
    if district:
        select_personalized_requests_query += " AND R.District = %s"
        filters.append(district)
    if hospital:
        select_personalized_requests_query += " AND R.Hospital = %s"
        filters.append(hospital)
    if status:
        select_personalized_requests_query += " AND R.Status = %s"
        filters.append(status)
    if request_id:
        select_personalized_requests_query += " AND R.Request_ID = %s"
        filters.append(request_id)
    
    try:
        # Connect to the database
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400

        user_blood_type = user["Blood_Type"]
        user_city = user["City"]
        user_district = user["District"]
        user_tc_id = user["TC_ID"]
        
        filters[0] = user_tc_id
        filters[1] = user_tc_id
        
        # Adding ordering logic for personalized results
        select_personalized_requests_query += """
            ORDER BY
                CASE
                    WHEN R.Blood_Type = %s AND R.City = %s AND R.District = %s THEN 1
                    WHEN R.Blood_Type = %s AND R.City = %s THEN 2
                    WHEN R.Blood_Type = %s THEN 3
                    WHEN R.City = %s AND R.District = %s THEN 4
                    WHEN R.City = %s THEN 5
                    ELSE 6
                END,
                R.Create_Time DESC;
        """
        
        filters.extend([
            user_blood_type, user_city, user_district,
            user_blood_type, user_city,
            user_blood_type,
            user_city, user_district,
            user_city
        ])
        
        # Execute the query with filters
        cursor.execute(select_personalized_requests_query, filters)
        
        results = cursor.fetchall()
        
        # Format the Create_Time column
        for row in results:
            row['Create_Time'] = row['Create_Time'].strftime('%Y-%m-%d %H:%M:%S')

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
    print(request.headers)
    user_id = request.headers.get("Authorization")
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400
    
    if not user_id:
        return jsonify({"error": "InvalidInput", "message": "User ID is required."  }), 400
    
    required_fields = ["donor_count", "location", "hospital", "status", "gender"]

    if "patient_tc_id" not in data:
        required_fields.append("blood_type")
        required_fields.append("age")
        required_fields.append("patient_name")
        required_fields.append("patient_surname")
        

    for field in required_fields:
        if field not in data:
            return jsonify({"error": "InvalidInput", "message": f"The '{field}' field is required."}), 400

    requested_tc_id = ""
    patient_tc_id = data.get("patient_tc_id")
    blood_type = data["blood_type"]
    age = data.get("age")
    gender = data.get("gender")
    note = data.get("note")
    donor_count = data["donor_count"]
    location = data["location"]              #location is a dictionary
    patient_name = data.get("patient_name") 
    patient_surname = data.get("patient_surname")
    hospital = data["hospital"]
    status = data["status"]
    create_time = datetime.now()
    
    city = location.get("city")
    district = location.get("district")
    lat= location.get("lat")
    lng = location.get("lng")
    print(lat)
    print(lng)

    try:
        connection = get_db()
        cursor = connection.cursor()
        
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400


        requested_tc_id = user[1]

        if patient_tc_id is None or patient_tc_id == "" or patient_tc_id == 0:
            patient_tc_id = requested_tc_id
            birth_date = user[4] 
            age = datetime.now().year - birth_date.year
            blood_type = user[8]
            patient_name = user[5]
            patient_surname = user[6]

        # check_location_query = "SELECT COUNT(*) FROM Locations WHERE City_Name = %s AND District_Name = %s"
        # cursor.execute(check_location_query, (city, district))
        # location_result = cursor.fetchone()

        # if location_result[0] == 0:
        #     return jsonify({"error": "InvalidInput", "message": "Invalid location."}), 400

        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-']
        if blood_type not in valid_blood_types:
            return jsonify({"error": "InvalidInput", "message": "Invalid blood type provided."}), 400

        # check_spam_query = "SELECT COUNT(*) FROM Requests WHERE Requested_TC_ID = %s AND Patient_TC_ID = %s AND Status = %s"
        # cursor.execute(check_spam_query, (requested_tc_id, patient_tc_id, status))
        # spam_result = cursor.fetchone()

        # if spam_result[0] > 3:
        #     return jsonify({"error": "InvalidInput", "message": "Duplicate request detected. Spam prevention triggered."}), 400

        insert_query = """
            INSERT INTO Requests (
                Requested_TC_ID, Patient_TC_ID, Blood_Type, Age, Gender, Note,
                Lat, Lng, City, District, Hospital, Status, Create_Time, Donor_Count, Patient_Name, Patient_Surname
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            requested_tc_id, patient_tc_id, blood_type, age, gender, note,
            lat, lng, city, district, hospital, status, create_time, donor_count, patient_name, patient_surname
        )

        cursor.execute(insert_query, values)  
        
        request_id = cursor.lastrowid
        notification_type = "Blood Request"
        message = f"Urgent blood request for {patient_name} {patient_surname}"
        common_params = {"blood": blood_type, "location": district + "/" + city + ", " + hospital, "timeout": "24 saat içinde", "contact": "kanver400@gmail.com"}

        notification_result = create_notification_logic(request_id, notification_type, message, common_params, connection)

        connection.commit()  
        
        return jsonify({
            "message": "Request created and notification sent successfully.",
            "request_id": request_id,
            "notification_id": notification_result["notification_id"]
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
