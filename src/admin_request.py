from datetime import datetime
from flask import Blueprint, jsonify, request
from mysql.connector import Error
from database.connection import get_db
from src.middleware import auth_required

admin_request_bp = Blueprint('admin_request', __name__)

@admin_request_bp.route('/admin_request/<int:request_id>', methods=['DELETE'])
#@auth_required
def delete_request(request_id):
    print(request.headers)
    # Extract user_id from "Authorization" header
    user_id = request.headers.get('Authorization')

    # Check if user_id matches the authorized ID
    if user_id != "QjfkPHy94WPNsHrR3IckSkXjEV42":
        return jsonify({"error": "Unauthorized access"}), 403

    # Connect to the database
    db = get_db()
    cursor = db.cursor()

    try:
        # Check if the request exists
        cursor.execute("SELECT * FROM Requests WHERE Request_ID = %s", (request_id,))
        request_data = cursor.fetchone()

        if not request_data:
            return jsonify({"error": "Request not found"}), 404

        # Delete the request
        cursor.execute("DELETE FROM Requests WHERE Request_ID = %s", (request_id,))
        db.commit()

        return jsonify({"message": f"Request with ID {request_id} has been deleted successfully."}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()
    
@admin_request_bp.route('/test', methods=['GET'])
def test():
    print("Test endpoint hit!")
    return jsonify({"message": "Admin request blueprint is working!"})

