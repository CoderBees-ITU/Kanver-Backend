from flask import Blueprint, request, jsonify
import mysql.connector
from database.connection import get_db

banned_bp = Blueprint('banned', __name__)

@banned_bp.route('/ban_user', methods=['POST'])
def ban_user():
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400

    # Gerekli alanlar
    required_fields = ["tc_id", "cause", "unban_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "InvalidInput", "message": f"Missing field: {field}"}), 400

    tc_id = data['tc_id']
    cause = data['cause']
    unban_date = data['unban_date']
    ban_date = data.get('ban_date', None)

    try:
        connection = get_db()
        cursor = connection.cursor()

        check_user_query = "SELECT COUNT(*) FROM User WHERE TC_ID = %s"
        cursor.execute(check_user_query, (tc_id,))
        user_exists = cursor.fetchone()[0]

        if not user_exists:
            return jsonify({"error": "NotFound", "message": "User not found."}), 404

        # Banned_Users tablosuna ekle
        insert_query = """
            INSERT INTO Banned_Users (TC_ID, Date, Cause, Unban_Date)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (tc_id, ban_date, cause, unban_date))
        connection.commit()
        
        return jsonify({"message": "User banned successfully."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
        

@banned_bp.route('/unban_user/<int:tc_id>', methods=['DELETE'])
def unban_user(tc_id):
    try:
        connection = get_db()
        cursor = connection.cursor()

        check_banned_query = "SELECT COUNT(*) FROM Banned_Users WHERE TC_ID = %s"
        cursor.execute(check_banned_query, (tc_id,))
        banned_exists = cursor.fetchone()[0]

        if not banned_exists:
            return jsonify({"error": "NotFound", "message": "User is not banned."}), 404

        # Banned_Users tablosundan kaydı sil
        delete_banned_query = "DELETE FROM Banned_Users WHERE TC_ID = %s"
        cursor.execute(delete_banned_query, (tc_id,))
        connection.commit()

        return jsonify({"message": "User unbanned successfully."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()

@banned_bp.route('/banned_users', methods=['GET'])
def get_all_banned_users():
    
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT BU.TC_ID, U.Name, U.Surname, U.Email, BU.Date, BU.Cause, BU.Unban_Date
            FROM Banned_Users BU
            JOIN User U ON BU.TC_ID = U.TC_ID
        """
        cursor.execute(query)
        banned_users = cursor.fetchall()

        if not banned_users:
            return jsonify({"message": "No banned users found."}), 404

        return jsonify(banned_users), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
