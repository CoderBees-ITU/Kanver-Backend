from flask import Blueprint, request, jsonify
import mysql.connector
from database.connection import get_db
from src.middleware import auth_required

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

        if blood_request['Status'] != 'Pending':
            return jsonify({"error": "RequestClosed", "message": "This blood request is no longer open."}), 400

        # Add a record to the On_The_Way table
        insert_on_the_way_query = """
            INSERT INTO On_The_Way (Request_ID, Donor_TC_ID, Status)
            VALUES (%s, %s, 'On The Way')
        """
        cursor.execute(insert_on_the_way_query, (request_id, donor_tc_id))

        # Commit the changes
        connection.commit()

        return jsonify({"message": "Donor successfully marked as on the way."}), 201

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

@on_the_way_bp.route('/on_the_way/<int:request_id>', methods=['PUT'])
#@auth_required
def update_on_the_way_status(request_id):
    data = request.get_json()
    user_id = request.headers.get("Authorization")

    if not data or 'status' not in data:
        return jsonify({"error": "InvalidInput", "message": "Status is required."}), 400

    new_status = data['status']

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        check_user_query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))

        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "InvalidInput", "message": "user_id of requester is not found in the database."}), 400

        donor_tc_id = user["TC_ID"]

        # Update the status of the donor in the On_The_Way table
        update_query = """
            UPDATE On_The_Way
            SET Status = %s
            WHERE Request_ID = %s AND Donor_TC_ID = %s
        """
        cursor.execute(update_query, (new_status, request_id, donor_tc_id))

        # Check if the update affected any rows
        if cursor.rowcount == 0:
            return jsonify({"error": "NotFound", "message": "No matching record found to update."}), 404

        if new_status == "Donated":
            decrement_donor_count_query = """
                UPDATE Requests
                SET Donor_Count = Donor_Count - 1
                WHERE Request_ID = %s
            """
        
            cursor.execute(decrement_donor_count_query, (request_id,))

        # Commit the changes
        connection.commit()

        return jsonify({"message": "Status updated successfully."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
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
