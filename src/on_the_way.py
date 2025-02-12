from flask import Blueprint, request, jsonify
import mysql.connector
from database.connection import get_db
from src.middleware import auth_required
from src.notification import create_notification_logic_on_the_way

on_the_way_bp = Blueprint('on_the_way', __name__)

@on_the_way_bp.route('/on_the_way', methods=['POST'])
#@auth_required
def add_on_the_way():
    data = request.get_json()
    user_id = request.headers.get("Authorization")

    if not data or 'request_id' not in data or not user_id:
        return jsonify({"error": "InvalidInput", "message": "Request ID and valid User_ID are required."}), 400

    request_id = data['request_id']

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400

        donor_tc_id = user["TC_ID"]
        
        check_existing_tc_query = "SELECT Donor_TC_ID FROM On_The_Way WHERE Request_ID = %s AND Donor_TC_ID = %s"
        cursor.execute(check_existing_tc_query, (request_id, donor_tc_id,))
        donor_request_exists = cursor.fetchone()
        
        if donor_request_exists:
            return jsonify({"error": "InvalidOnTheWay", "message": "This Donor TC ID was already used for this blood request"}), 400

        # Check if the donor exists and is eligible
        check_donor_query = "SELECT Is_Eligible FROM User WHERE TC_ID = %s"
        cursor.execute(check_donor_query, (donor_tc_id,))
        donor = cursor.fetchone()

        if not donor:
            return jsonify({"error": "NotFound", "message": "Donor not found in the database."}), 404

        if not donor['Is_Eligible']:
            return jsonify({"error": "NotEligible", "message": "Donor is not eligible to donate blood."}), 400

        # Check if the request exists and is still open
        check_request_query = "SELECT Status, Donor_Count FROM Requests WHERE Request_ID = %s"
        cursor.execute(check_request_query, (request_id,))
        blood_request = cursor.fetchone()

        if not blood_request:
            return jsonify({"error": "NotFound", "message": "Request not found in the database."}), 404

        if blood_request['Status'] != 'pending':
            return jsonify({"error": "RequestClosed", "message": "This blood request is no longer open."}), 400

        # Add a record to the On_The_Way table
        insert_on_the_way_query = """
            INSERT INTO On_The_Way (Request_ID, Donor_TC_ID, Status)
            VALUES (%s, %s, 'on_the_way')
        """
        cursor.execute(insert_on_the_way_query, (request_id, donor_tc_id))
        connection.commit()
        
        on_the_way_id = cursor.lastrowid
        notification_type="on the way"
        message = f"{user['Name']} {user['Surname']} {request_id} id'li istek için yola çıktı"
        
        create_notification_logic_on_the_way(on_the_way_id,notification_type,message,connection)
        return jsonify({"message": "Donor successfully marked as on the way."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@on_the_way_bp.route('/on_the_way/<int:request_id>', methods=['DELETE'])
#@auth_required
def cancel_on_the_way(request_id):
    user_id = request.headers.get("Authorization")
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400

        donor_tc_id = user["TC_ID"]

        # Check if the record exists in the On_The_Way table
        check_on_the_way_query = """
            SELECT * FROM On_The_Way
            WHERE Request_ID = %s AND Donor_TC_ID = %s
        """
        cursor.execute(check_on_the_way_query, (request_id, donor_tc_id))
        on_the_way_record = cursor.fetchone()

        if not on_the_way_record:
            return jsonify({"error": "NotFound", "message": "No matching record found for this donor and request."}), 404

        # Delete the record from the On_The_Way table
        delete_on_the_way_query = """
            DELETE FROM On_The_Way
            WHERE Request_ID = %s AND Donor_TC_ID = %s
        """
        cursor.execute(delete_on_the_way_query, (request_id, donor_tc_id))

        # Commit the changes
        connection.commit()

        return jsonify({"message": "Donor successfully removed from on-the-way status."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@on_the_way_bp.route('/on_the_way/<int:request_id>', methods=['GET'])
#@auth_required
def get_on_the_way(request_id):
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Query to fetch all donors for the given request ID
        query = """
            SELECT * FROM On_The_Way
            WHERE Request_ID = %s
        """
        cursor.execute(query, (request_id,))
        donors = cursor.fetchall()

        if not donors:
            return jsonify({"error": "NotFound", "message": "No donors found for the given request ID."}), 404

        return jsonify(donors), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        
@on_the_way_bp.route('/on_the_way/my', methods=['GET'])
# @auth_required
def get_my_on_the_way_requests():
    # Retrieve filter parameters from query arguments
    patient_tc_id = request.args.get("patient_tc_id")
    blood_type = request.args.get("blood_type")
    age = request.args.get("age")
    gender = request.args.get("gender")
    city = request.args.get("city")
    district = request.args.get("district")
    hospital = request.args.get("hospital")
    status = request.args.get("status")
    request_id = request.args.get("request_id")

    # Retrieve the user_id from Authorization header
    user_id = request.headers.get("Authorization")
    if not user_id:
        return jsonify({"error": "InvalidInput", "message": "User ID is required."}), 400

    try:
        # Connect to the database
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Verify if the user exists and retrieve user_tc_id
        check_user_query = "SELECT TC_ID FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "User ID not found in the database."}), 400
        user_tc_id = user["TC_ID"]

        # Base query to fetch requests and associated on_the_way records
        query = """
            SELECT 
                Requests.*, 
                On_The_Way.*, 
                (SELECT COUNT(*) 
                 FROM On_The_Way 
                 WHERE On_The_Way.Request_ID = Requests.Request_ID) AS On_The_Way_Count
            FROM 
                On_The_Way
            INNER JOIN 
                Requests 
            ON 
                On_The_Way.Request_ID = Requests.Request_ID
            WHERE 
                On_The_Way.Donor_TC_ID = %s
        """
        filters = [user_tc_id]

        # Add dynamic filters to the query
        if patient_tc_id:
            query += " AND Requests.Patient_TC_ID = %s"
            filters.append(patient_tc_id)
        if blood_type:
            query += " AND Requests.Blood_Type = %s"
            filters.append(blood_type.strip())
        if age:
            query += " AND Requests.Age = %s"
            filters.append(age)
        if gender:
            query += " AND Requests.Gender = %s"
            filters.append(gender)
        if city:
            query += " AND Requests.City = %s"
            filters.append(city)
        if district:
            query += " AND Requests.District = %s"
            filters.append(district)
        if hospital:
            query += " AND Requests.Hospital = %s"
            filters.append(hospital)
        if status:
            query += " AND Requests.Status = %s"
            filters.append(status)
        if request_id:
            query += " AND Requests.Request_ID = %s"
            filters.append(request_id)

        # Add sorting
        query += " ORDER BY Requests.Create_Time DESC"

        # Execute the query
        cursor.execute(query, filters)
        records = cursor.fetchall()

        if not records:
            return jsonify({"error": "NotFound", "message": "No requests found for the given user."}), 404

        # Format the Create_Time column for each record
        for record in records:
            if 'Create_Time' in record and record['Create_Time']:
                record['Create_Time'] = record['Create_Time'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(records), 200

    except mysql.connector.Error as err:
        # Handle database errors
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        # Ensure the cursor and connection are properly closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@on_the_way_bp.route('/on_the_way/<int:on_the_way_id>', methods=['PUT'])
def update_on_the_way_status(on_the_way_id):
    data = request.get_json()
    user_id = request.headers.get("Authorization")  

    if not data or 'status' not in data or 'request_id' not in data:
        return jsonify({
            "error": "InvalidInput",
            "message": "Both 'status' and 'request_id' fields are required in JSON."
        }), 400

    new_status = data['status'].strip().lower()
    request_id = data['request_id']

    # 2. Validate the Authorization header (optional, but recommended)
    if not user_id:
        return jsonify({
            "error": "InvalidInput",
            "message": "Missing Authorization header."
        }), 400

    # 3. Attempt DB operations
    connection = None
    cursor = None
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # 3a. Check if the user exists
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        user_record = cursor.fetchone()
        if not user_record:
            return jsonify({
                "error": "InvalidInput",
                "message": "User with given user_id not found in the database."
            }), 400

        requester_tc_id = user_record["TC_ID"]

        # 3b. Check if the request record exists
        check_request_query = "SELECT * FROM Requests WHERE Request_ID = %s"
        cursor.execute(check_request_query, (request_id,))
        request_record = cursor.fetchone()
        if not request_record:
            return jsonify({
                "error": "NotFound",
                "message": "Request not found in the database."
            }), 404

        # 3c. Check if the user is authorized to update this request
        if request_record['Requested_TC_ID'] != requester_tc_id:
            return jsonify({
                "error": "NotAuthorized",
                "message": "You are not authorized to update this request."
            }), 403

        # 3d. Update the On_The_Way record
        update_query = """
            UPDATE On_The_Way
               SET Status = %s
             WHERE ID = %s
               AND Request_ID = %s
        """
        cursor.execute(update_query, (new_status, on_the_way_id, request_id))

        # If no rows were updated, the record wasn't found or didn't match the filter
        if cursor.rowcount == 0:
            return jsonify({
                "error": "NotFound",
                "message": "No matching On_The_Way record found to update."
            }), 404

        # 3e. If status is 'completed', decrement the donor count for that request
        if new_status == "completed":
            decrement_donor_count_query = """
                UPDATE Requests
                   SET Donor_Count = Donor_Count - 1
                 WHERE Request_ID = %s
            """
            cursor.execute(decrement_donor_count_query, (request_id,))
            
            get_donor_user_id_query = """
                SELECT User.User_id
                FROM On_The_Way
                INNER JOIN User ON On_The_Way.Donor_TC_ID = User.TC_ID
                WHERE On_The_Way.ID = %s
            """
            cursor.execute(get_donor_user_id_query, (on_the_way_id,))
            donor_user_id = cursor.fetchone()
            donor_user_id = donor_user_id['User_id']
            
            update_user_is_eligible_query = """
                UPDATE User
                SET Is_Eligible = FALSE, Last_Donation_Date = CURRENT_TIMESTAMP
                WHERE User_id = %s
            """
            cursor.execute(update_user_is_eligible_query, (donor_user_id,))

        # 3f. Check whether the request now has zero donors left
        check_request_completed_query = """
            SELECT Donor_Count 
              FROM Requests 
             WHERE Request_ID = %s
        """
        cursor.execute(check_request_completed_query, (request_id,))
        updated_request_record = cursor.fetchone()

        if updated_request_record and updated_request_record['Donor_Count'] == 0:
            # Mark the entire request as completed
            update_request_status_query = """
                UPDATE Requests
                   SET Status = 'completed'
                 WHERE Request_ID = %s
            """
            cursor.execute(update_request_status_query, (request_id,))

        # 3g. Commit the changes
        connection.commit()

        return jsonify({
            "message": "Status updated successfully."
        }), 200

    except mysql.connector.Error as err:
        # Handle any MySQL-related errors
        return jsonify({
            "error": "DatabaseError",
            "message": f"Database error: {err}"
        }), 500

    finally:
        # 3h. Close DB cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@on_the_way_bp.route('/on_the_way/my', methods=['GET'])
# @auth_required
def get_on_the_way_my():
    user_id = request.headers.get("Authorization")
    if not user_id:
        return jsonify({"error": "InvalidInput", "message": "Authorization header is missing."}), 400

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Validate user existence
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "InvalidInput", "message": "User ID is not found in the database."}), 400

        user_tc_id = user["TC_ID"]

        # Fetch requests where the user is a donor
        query = """
            SELECT 
                otw.ID AS on_the_way_id,
                otw.Status AS on_the_way_status,
                otw.Create_Time AS on_the_way_time,
                r.Request_ID,
                r.Blood_Type,
                r.City,
                r.District,
                r.Hospital,
                r.patient_name,
                r.patient_surname,
                r.Gender,
                r.Note,
                r.Create_Time AS request_time
            FROM 
                On_The_Way otw
            INNER JOIN 
                Requests r ON otw.Request_ID = r.Request_ID
            WHERE 
                otw.Donor_TC_ID = %s
            ORDER BY 
                otw.Create_Time DESC
        """
        cursor.execute(query, (user_tc_id,))
        requests = cursor.fetchall()

        if not requests:
            return jsonify({"error": "NotFound", "message": "No requests found for the user."}), 404

        return jsonify({"requests": requests}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
