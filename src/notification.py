from flask import Blueprint, request, jsonify
from database.connection import get_db
import mysql.connector

import json
import requests


notification_bp = Blueprint("notification", __name__)

API_KEY = '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'
SENDER_EMAIL = "kul3562@gmail.com"
SENDER_NAME = "KANVER"
TEMPLATE_ID = 2 

def send_email(common_params, recipients):
    """
    Brevo API ile toplu e-posta gönderimi yapan fonksiyon.
    
    Args:
        common_params (dict): Tüm alıcılar için geçerli ortak parametreler.
        recipients (list): Alıcıların e-posta adresleri ve isim bilgileri listesi.
    """
    message_versions = []
    for recipient in recipients:
        message_versions.append({
            "to": [{"email": recipient["email"], "name": recipient["name"]}],
            "params": {**common_params, "receiverName": recipient["name"]},
            "subject": "Acil Kan İhtiyacı" 
        })

    payload = {
        "sender": {
            "email": SENDER_EMAIL,
            "name": SENDER_NAME
        },
        "templateId": TEMPLATE_ID,
        "messageVersions": message_versions
    }

    # Brevo'ya POST isteği gönderimi
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "content-type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Yanıtı döndür
    if response.status_code == 201:
        print("E-postalar başarıyla gönderildi!")
        return response.json()
    else:
        print(f"Hata! Status Code: {response.status_code}")
        print(response.text)
        return None

def create_notification_logic(request_id, notification_type, message, common_params, db_connection):
    location = common_params["location"]
    location_parts = location.split(", ")
    district_city = location_parts[0]
    hospital = location_parts[1]
    district_city_parts = district_city.split("/")
    
    district = district_city_parts[0]
    city = district_city_parts[1]
    try:
        cursor = db_connection.cursor(dictionary=True)

        # Query users with matching blood type
        query = """
            SELECT 
                CONCAT(Name, ' ', Surname) AS fullName,
                Email 
            FROM 
                User
            WHERE 
                Blood_Type = %s AND City = %s AND District = %s
        """
        cursor.execute(query, (common_params["blood"], city, district,))
        tmp_recipients = cursor.fetchall()

        # Prepare recipients list
        recipients = [{"email": recipient["Email"], "name": recipient["fullName"]} for recipient in tmp_recipients]

        # Insert notification into Notifications table
        insert_query = """
            INSERT INTO Notifications (Request_ID, Notification_Type, Message)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (request_id, notification_type, message))
        db_connection.commit()

        # Get the notification ID
        notification_id = cursor.lastrowid
        common_params["locations"] = hospital

        # Send email
        send_email(common_params, recipients)

        return {
            "notification_id": notification_id,
            "recipients": recipients
        }

    except Exception as e:
        raise Exception(f"Notification error: {str(e)}")

    finally:
        cursor.close()



@notification_bp.route("/create", methods=["POST"])
def create_notification():
    data = request.get_json()
    if not data:
        return jsonify({"error": "InvalidInput", "message": "No input data provided"}), 400

    # Gerekli alanlar
    required_fields = ["request_id", "notification_type", "message", "common_params"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "InvalidInput", "message": f"Missing field: {field}"}), 400

    request_id = data["request_id"]
    notification_type = data["notification_type"]
    message = data["message"]
    common_params = data["common_params"]

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        # Kan grubu eşleşen alıcıları sorgula
        query = """
            SELECT 
            CONCAT(Name, ' ', Surname) AS fullName, Email
            FROM 
            User left join Banned_Users on
            User.TC_ID = Banned_Users.TC_ID
            where
            Banned_Users.TC_ID is null and
            Blood_Type = %s and is_Eligible=True;
        """
        cursor.execute(query, (common_params["blood"],))
        tmp_recipients = cursor.fetchall()

        # Alıcı listesi oluştur
        recipients = [{"email": recipient["Email"], "name": recipient["fullName"]} for recipient in tmp_recipients]

        # Bildirimi Notifications tablosuna ekle
        insert_query = """
            INSERT INTO Notifications (Request_ID, Notification_Type, Message, Total_Mail_Sent)
            VALUES (%s, %s, %s,%s)
        """
        cursor.execute(insert_query, (request_id, notification_type, message,len(tmp_recipients)))
        connection.commit()

        notification_id = cursor.lastrowid

        # E-postayı gönder
        send_email(common_params, recipients)

        return jsonify({
            "message": "Notification created and email sent successfully.",
            "notification_id": notification_id
        }), 201

    except Exception as e:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {str(e)}"}), 500

    finally:
        cursor.close()
        connection.close()


@notification_bp.route("/notifications", methods=["get"])
def get_notifications():
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM Notifications"
        cursor.execute(query)
        notifications = cursor.fetchall()


        if not notifications:
            return jsonify({"error": "NotFound", "message": "No notifications found in the database."}), 404

        return jsonify(notifications), 200

    except mysql.connector.Error as err:
        return jsonify({"error": "DatabaseError", "message": f"Database error: {err}"}), 500

    finally:
        cursor.close()
        connection.close()
