import logging
from datetime import datetime

import pytest
from flask import json

from database.connection import get_db

logger = logging.getLogger(__name__)
payload = {
        "email": "test@example.com",
        "password": "securepassword",
        "name": "Test",
        "surname": "User",
        "tc": "12345678901",
        "blood_type": "0+",
        "birth_date" : "1992-03-15"
}

# Test 0 : Ban an existing user
# Test 1 : Ban a non-existing user
# Test 2 : Ban a user with missing fields (tc_id, cause, unban_date)
# Test 3 : Ban an already banned user
# Test 4 : Unban an existing user
# Test 5 : Unban a non-banned user
# Test 6 : Get all banned users
# Test 7 : Get all banned users when there are no banned users

def test_ban_existing_user_success(client, db_connection, truncate_table, mock_firebase):
    # Clear the User and Banned_Users tables
    truncate_table("User")
    truncate_table("Banned_Users")
    
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"
    
    # Now, ban the user
    ban_payload = {
        "tc_id": "12345678901",
        "cause": "Violation of terms",
        "unban_date": "2025-01-01"
    }
    
    response = client.post("/ban_user", json=ban_payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User banned successfully."
    
    # Verify the ban in the database
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Banned_Users WHERE TC_ID = %s", ("12345678901",))
    banned_user = cursor.fetchone()
    cursor.close()
    
    assert banned_user is not None
    assert banned_user["Cause"] == "Violation of terms"
    assert banned_user["Unban_Date"].strftime('%Y-%m-%d') == "2025-01-01"

def test_ban_non_existing_user(client, db_connection, truncate_table):
    truncate_table("User")
    truncate_table("Banned_Users")
    
    ban_payload = {
        "tc_id": "99999999999",
        "cause": "Spamming",
        "unban_date": "2025-01-01"
    }
    
    response = client.post("/ban_user", json=ban_payload)
    response_data = response.get_json()
    
    assert response.status_code == 404
    assert response_data["error"] == "NotFound"
    assert response_data["message"] == "User not found."
    
@pytest.mark.parametrize("missing_field", ["tc_id", "cause", "unban_date"])
def test_ban_user_missing_fields(client, db_connection, truncate_table, missing_field, mock_firebase):
    truncate_table("User")
    truncate_table("Banned_Users")
    
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"
    
    ban_payload = {
        "tc_id": "12345678901",
        "cause": "Violation of terms",
        "unban_date": "2025-01-01"
    }
    
    del ban_payload[missing_field]
    
    response = client.post("/ban_user", json=ban_payload)
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data["error"] == "InvalidInput"
    assert response_data["message"] == f"Missing field: {missing_field}"

# Not handled in the banned_user endpoint
# def test_ban_user_already_banned(client, db_connection, truncate_table, mock_firebase):
#     # Clear the User and Banned_Users tables
#     truncate_table("User")
#     truncate_table("Banned_Users")
    
#     response = client.post("/register", json=payload)
#     response_data = response.get_json()
    
#     assert response.status_code == 200
#     assert response_data["message"] == "User created successfully"
    
#     # First ban
#     ban_payload = {
#         "tc_id": "12345678901",
#         "cause": "Violation of terms",
#         "unban_date": "2025-01-01"
#     }
    
#     response = client.post("/ban_user", json=ban_payload)
#     response_data = response.get_json()
    
#     assert response.status_code == 200
#     assert response_data["message"] == "User banned successfully."
    
#     # Attempt to ban again
#     response = client.post("/ban_user", json=ban_payload)
#     response_data = response.get_json()

#     # If duplicates are allowed:
#     assert response.status_code == 200
#     assert response_data["message"] == "User banned successfully."
    
#     # If duplicates are not allowed and you implemented checks:
#     # assert response.status_code == 409
#     # assert response_data["error"] == "Conflict"
#     # assert response_data["message"] == "User is already banned."

def test_unban_existing_user_success(client, db_connection, truncate_table, mock_firebase):
    truncate_table("User")
    truncate_table("Banned_Users")
    
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"
    
    ban_payload = {
        "tc_id": "12345678901",
        "cause": "Violation of terms",
        "unban_date": "2025-01-01"
    }
    
    response = client.post("/ban_user", json=ban_payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User banned successfully."
    
    response = client.delete("/unban_user/12345678901")
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User unbanned successfully."
    
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Banned_Users WHERE TC_ID = %s", ("12345678904",))
    banned_user = cursor.fetchone()
    cursor.close()
    
    assert banned_user is None
    
def test_unban_non_banned_user(client, db_connection, truncate_table, mock_firebase):
    truncate_table("User")
    truncate_table("Banned_Users")
    
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"
    
    response = client.delete("/unban_user/12345678901")
    response_data = response.get_json()
    
    assert response.status_code == 404
    assert response_data["error"] == "NotFound"
    assert response_data["message"] == "User is not banned."

def test_get_banned_users_success(client, db_connection, truncate_table, mock_firebase):
    truncate_table("User")
    truncate_table("Banned_Users")
    
    users = [
        {
            "email": "banned1@example.com",
            "password": "securepassword",
            "name": "Banned",
            "surname": "User1",
            "tc": 12345678901,
            "blood_type": "AB-",
            "birth_date": "1995-06-06"
        },
        {
            "email": "banned2@example.com",
            "password": "securepassword",
            "name": "Banned",
            "surname": "User2",
            "tc": 12345678902,
            "blood_type": "A-",
            "birth_date": "1996-07-07"
        }
    ]
    
    for user in users:
        response = client.post("/register", json=user)
        response_data = response.get_json()
        assert response.status_code == 200
        assert response_data["message"] == "User created successfully"
        
        ban_payload = {
            "tc_id": user["tc"],
            "cause": "Violation of terms",
            "unban_date": "2025-01-01"
        }
        
        response = client.post("/ban_user", json=ban_payload)
        response_data = response.get_json()
        assert response.status_code == 200
        assert response_data["message"] == "User banned successfully."
    
    response = client.get("/banned_users")
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data) == 2
    
    for banned_user, original_user in zip(response_data, users):
        assert banned_user["TC_ID"] == original_user["tc"]
        assert banned_user["Name"] == original_user["name"]
        assert banned_user["Surname"] == original_user["surname"]
        assert banned_user["Email"] == original_user["email"]
        assert banned_user["Cause"] == "Violation of terms"
        formatted_date = datetime.strptime(banned_user["Unban_Date"], '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d')
        assert formatted_date == "2025-01-01"

def test_get_banned_users_no_bans(client, db_connection, truncate_table, mock_firebase):
    truncate_table("User")
    truncate_table("Banned_Users")
    
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"
    
    response = client.get("/banned_users")
    response_data = response.get_json()
    
    assert response.status_code == 404
    assert response_data["message"] == "No banned users found."
