import json
import logging
from unittest.mock import MagicMock, patch

logger = logging.getLogger(__name__)
payload = {
        "email": "test@example.com",
        "password": "securepassword",
        "name": "Test",
        "surname": "User",
        "tc": "12345678901",
        "blood_type": "O+",
        "birth_date" : "1992-03-15"
}

def test_login_with_registered_user(client, db_connection, truncate_table, mock_firebase):
    # Clear the User and Banned_Users tables
    truncate_table("User")
    truncate_table("Banned_Users")

    # Register a user first
    response = client.post("/register", json=payload)
    response_data = response.get_json()

    # Assert user created successfully
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"

    # Login with the registered user's ID token
    login_payload = {"idToken": "mock_token"}  # Mock token from Firebase
    response = client.post("/login", json=login_payload)
    response_data = response.get_json()

    # Assert login successful
    assert response.status_code == 200
    assert response_data["message"] == "Login successful"
    assert response_data["user"]["email"] == payload["email"]
    assert response_data["user"]["name"] == payload["name"]
    assert response_data["user"]["surname"] == payload["surname"]


def test_login_with_unregistered_user(client, truncate_table, mock_firebase):
    # Clear the User table
    truncate_table("User")
    truncate_table("Banned_Users")

    # Attempt login without registering the user
    login_payload = {"idToken": "mock_token"}  # Mock token from Firebase
    response = client.post("/login", json=login_payload)
    response_data = response.get_json()

    # Assert user not found
    assert response.status_code == 404
    assert response_data["message"] == "User not found"

def test_login_with_invalid_token(client, db_connection, truncate_table, mock_firebase):
    # Clear the User table
    truncate_table("User")
    truncate_table("Banned_Users")

    # Register a user first
    response = client.post("/register", json=payload)
    response_data = response.get_json()

    # Assert user created successfully
    assert response.status_code == 200
    assert response_data["message"] == "User created successfully"

    # Attempt login with an invalid token
    login_payload = {"idToken": "invalid_token"}  # Invalid token
    response = client.post("/login", json=login_payload)
    response_data = response.get_json()

    # Assert invalid token error
    assert response.status_code == 401
    assert response_data["message"] == "Invalid ID token"

# ban user testleri henüz gelmedi onlardan sonra buna bakacağım
# def test_login_with_banned_user(client, db_connection, truncate_table, mock_firebase):
#     # Clear the User and Banned_Users tables
#     truncate_table("User")
#     truncate_table("Banned_Users")

#     # Register a user first
#     response = client.post("/register", json=payload)
#     response_data = response.get_json()

#     # Assert user created successfully
#     assert response.status_code == 200
#     assert response_data["message"] == "User created successfully"

#     # Ban the user
#     cursor = db_connection.cursor()
#     cursor.execute("""
#         INSERT INTO Banned_Users (TC_ID, Cause, Unban_Date)
#         VALUES (%s, %s, %s)
#     """, ("12345678901", "Violation of terms", "2025-01-01"))
#     db_connection.commit()

#     # Attempt login as the banned user
#     login_payload = {"idToken": "mock_token"}  # Mock token from Firebase
#     response = client.post("/login", json=login_payload)
#     response_data = response.get_json()

#     # Assert banned user error
#     assert response.status_code == 403
#     assert response_data["message"] == "User is banned"
#     assert response_data["ban_reason"] == "Violation of terms"
#     assert response_data["unban_date"] == "2025-01-01"
