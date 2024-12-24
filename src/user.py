from flask import Blueprint, request, jsonify
import mysql.connector
from database.connection import get_db

user_bp = Blueprint('user', __name__)
banned_bp = Blueprint('banned', __name__)

@user_bp.route("/users", methods=["GET"])
def get_all_users():
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM User"
        cursor.execute(query)
        users = cursor.fetchall()

        if not users:
            return jsonify({"error": "NotFound", "message": "No users found in the database."}), 404

        return jsonify(users), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()


@user_bp.route("/user/<int:tc_id>", methods=["GET"])
def get_user_by_tc(tc_id):

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM User WHERE TC_ID = %s"
        cursor.execute(query, (tc_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "NotFound", "message": "User not found with the given TC ID."}), 404

        return jsonify(user), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()

@user_bp.route("/users/count", methods=["GET"])
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
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()


@user_bp.route("/user/<int:tc_id>", methods=["PUT"])
def update_user(tc_id):

    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400

    #is_eligible şimdilik dursun duruma göre değiştirebiliriz
    updatable_fields = ["name", "surname", "email", "blood_type", "location", "last_donation_date", "is_eligible"]
    updates = []
    values = []

    for field in updatable_fields:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return jsonify({"error": "InvalidInput", "message": "No valid fields provided for update."}), 400


    query = f"UPDATE User SET {', '.join(updates)} WHERE TC_ID = %s"
    values.append(tc_id)

    try:
        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "NotFound", "message": "No user found with the given TC ID."}), 404

        return jsonify({"message": "User updated successfully."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
        
        
@user_bp.route('/delete_user/<int:tc_id>', methods=['DELETE'])
def delete_user(tc_id):
    try:
        connection = get_db()
        cursor = connection.cursor()

        check_user_query = "SELECT COUNT(*) FROM User WHERE TC_ID = %s"
        cursor.execute(check_user_query, (tc_id,))
        user_exists = cursor.fetchone()[0]

        if not user_exists:
            return jsonify({"error": "NotFound", "message": "User not found."}), 404

        # Kullanıcıyı silme
        delete_user_query = "DELETE FROM User WHERE TC_ID = %s"
        cursor.execute(delete_user_query, (tc_id,))
        connection.commit()
        
        #on delete cascade olduğu için gereksiz
        # delete_user_if_banned_query = "DELETE FROM Banned_user WHERE TC_ID = %s"
        # cursor.execute(delete_user_if_banned_query, (tc_id,))
        # connection.commit()

        return jsonify({"message": "User deleted successfully."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()

