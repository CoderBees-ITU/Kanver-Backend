from flask import Blueprint, request, jsonify
import mysql.connector
from database.connection import get_db
from firebase_admin import auth, app_check

user_bp = Blueprint('user', __name__)

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



@user_bp.route("/user/<string:user_id>", methods=["GET"])
def get_user_by_tc(user_id):

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM User WHERE user_id = %s"
        cursor.execute(query, (user_id,))
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
            "total": user_count
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()


@user_bp.route("/user/<string:user_id>", methods=["PUT"])
def update_user(user_id):

    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided."}), 400

    #is_eligible şimdilik dursun duruma göre değiştirebiliriz
    updatable_fields = ["name", "surname", "email", "blood_type", "city", "district", "last_donation_date", "is_eligible"]
    updates = []
    values = []

    for field in updatable_fields:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return jsonify({"error": "InvalidInput", "message": "No valid fields provided for update."}), 400


    query = f"UPDATE User SET {', '.join(updates)} WHERE user_id = %s"
    values.append(user_id)

    try:
        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "NotFound", "message": "No user found with the given user_id."}), 404

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
        cursor = connection.cursor(dictionary=True)

        # Check if the user exists in the database
        check_user_query = "SELECT * FROM User WHERE TC_ID = %s"
        cursor.execute(check_user_query, (tc_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "NotFound", "message": "User not found."}), 404

        # Delete the user from Firebase
        firebase_uid = user['User_id']  # Assuming 'User_id' is the Firebase UID
        try:
            auth.delete_user(firebase_uid)
        except auth.UserNotFoundError:
            return jsonify({"error": "FirebaseError", "message": "User not found in Firebase."}), 404

        # Delete the user from the database
        delete_user_query = "DELETE FROM User WHERE TC_ID = %s"
        cursor.execute(delete_user_query, (tc_id,))
        connection.commit()

        return jsonify({"message": "User deleted successfully from database and Firebase."}), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    except Exception as e:
        return jsonify({"error": "ServerError", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()