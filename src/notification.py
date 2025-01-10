from flask import Blueprint, request, jsonify
from database.connection import get_db
import mysql.connector
import os
import json
import requests

def convert_turkish_chars(text):
    turkish_to_english = str.maketrans({
        "ç": "c", "Ç": "C",
        "ğ": "g", "Ğ": "G",
        "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O",
        "ş": "s", "Ş": "S",
        "ü": "u", "Ü": "U"
    })
    return text.translate(turkish_to_english)


notification_bp = Blueprint("notification", __name__)

API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = "KANVER"

def send_email(common_params, recipients,templa_id):
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
        })

    payload = {
        "sender": {
            "email": SENDER_EMAIL,
            "name": SENDER_NAME
        },
        "templateId": templa_id,
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
    
    district_upper = district_city_parts[0].upper()
    city_upper = district_city_parts[1].upper()
    
    uni_district = convert_turkish_chars(district_upper)
    uni_city = convert_turkish_chars(city_upper)
    try:
        cursor = db_connection.cursor(dictionary=True)
 
        # Query users with matching blood type
        query = """
            SELECT 
                CONCAT(Name, ' ', Surname) AS fullName,
                Email 
            FROM 
                User left join Banned_Users on
                User.TC_ID = Banned_Users.TC_ID
            WHERE 
                Banned_Users.TC_ID is null and
                Blood_Type = %s AND (City = %s OR City = %s)AND (District = %s OR District = %s)
                and is_Eligible=True;
        """
        cursor.execute(query, (common_params["blood"], city_upper, uni_city,district_upper,uni_district))
        tmp_recipients = cursor.fetchall()

        # Prepare recipients list
        recipients = [{"email": recipient["Email"], "name": recipient["fullName"]} for recipient in tmp_recipients]

        # Insert notification into Notifications table
        insert_query = """
            INSERT INTO Notifications (Request_ID, Notification_Type, Message,Total_Mail_Sent)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (request_id, notification_type, message,len(recipients)))
        db_connection.commit()

        # Get the notification ID
        notification_id = cursor.lastrowid
        common_params["locations"] = hospital

        # Send email
        send_email(common_params, recipients,2)

        return {
            "notification_id": notification_id,
            "recipients": recipients
        }

    except Exception as e:
        raise Exception(f"Notification error: {str(e)}")

    finally:
        cursor.close()

def create_notification_logic_on_the_way(on_the_way_id, notification_type, message, db_connection):
    """
    'On The Way' butonuna tıklama sonrası bildirim ve e-posta işlemlerini yönetir.

    Args:
        on_the_way_id (int): On_The_Way tablosundaki ID.
        notification_type (str): Bildirim türü (ör. "OnTheWay").
        message (str): Bildirim mesajı.
        db_connection: Veritabanı bağlantı nesnesi.

    Returns:
        dict: Bildirim ID'si ve alıcılar hakkında bilgi.
    """
    try:
        cursor = db_connection.cursor(dictionary=True)

        # On_The_Way kaydını al
        query = """
            SELECT ow.Request_ID, r.Blood_Type, r.Hospital, r.City, r.District,
                   CONCAT(u1.Name, ' ', u1.Surname) AS DonorName,
                   u2.Name AS RequesterName, u2.Surname AS RequesterSurname, u2.Email AS RequesterEmail
            FROM On_The_Way ow
            JOIN Requests r ON ow.Request_ID = r.Request_ID
            JOIN User u1 ON ow.Donor_TC_ID = u1.TC_ID
            JOIN User u2 ON r.Requested_TC_ID = u2.TC_ID
            WHERE ow.ID = %s
        """
        cursor.execute(query, (on_the_way_id,))
        result = cursor.fetchone()

        if not result:
            raise Exception("On_The_Way kaydı bulunamadı.")

        # Bildirim bilgileri hazırlama
        request_id = result["Request_ID"]
        hospital = result["Hospital"]
        city = result["City"]
        district = result["District"]

        common_params = {
            "blood": result["Blood_Type"],
            "locations": f"{district}/{city}, {hospital}",
            "donorName": result["DonorName"],
            "contact": "kanver400@gmail.com"
            
        }

        # Alıcı bilgileri
        recipients = [
            {"email": result["RequesterEmail"], "name": f"{result['RequesterName']} {result['RequesterSurname']}"}
        ]

        # Bildirimi Notifications tablosuna ekle
        insert_query = """
            INSERT INTO Notifications (Request_ID, Notification_Type, Message,Total_Mail_Sent)
            VALUES (%s, %s, %s,1)
        """
        cursor.execute(insert_query, (request_id, notification_type, message))
        db_connection.commit()

        notification_id = cursor.lastrowid

        print("tebriks")
        send_email(common_params, recipients,3)

        return {
            "notification_id": notification_id,
            "recipients": recipients
        }

    except Exception as e:
        raise Exception(f"Notification error: {str(e)}")

    finally:
        cursor.close()

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
