import logging
import json
from unittest.mock import MagicMock
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
# Test 0 : User Creation
# Test 1 : Duplicate User Creation
# Test 2 : User Creation with Missing Fields from UserRegister Model (Email and name missing)
# Test 3 : User Creation with False Fields from UserRegister Model (TC = 1234)

def test_user_creation_with_clean_table(client, db_connection ,truncate_table,mock_firebase):
    # Clear the table
    truncate_table("User")

    # Perform user creation
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    
    # Assert user created successfully
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["message"] == "User created successfully"
    # Validate the database state
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM User WHERE Email = %s", ("test@example.com",))
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "test_user_id"

def test_user_already_exists(client,db_connection, truncate_table,mock_firebase):
    # Clear the table first
    truncate_table("User")

    # Insert a user
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    assert response.status_code == 200

    response = client.post("/register", json=payload)
    response_data = response.get_json()

    # Assert user already exists error
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["message"] == "User already exists"
    # Validate the database state
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM User WHERE Email = %s", ("test@example.com",))
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "test_user_id"



def test_user_creation_with_missing_field(client, db_connection ,truncate_table,mock_firebase):
    # Clear the table
    truncate_table("User")

    missing_field_payload = {k : v for k,v in payload.items() if k not in ["email", "name"]}
    
    # Perform user creation
    response = client.post("/register", json=missing_field_payload)
    response_data = response.get_json()
    # logger.debug("Response Data:\n%s", json.dumps(response_data, indent=4))
    
    # Assert missing fields 
    assert response.status_code == 400, "Should return 400 bad request on validation error"
    assert "validation_error" in response_data, "Response should have validation_error"
    assert len(response_data["validation_error"]["body_params"]) == 2, "Two missing fields needs to be detected"
    
def test_user_creation_with_false_field(client, db_connection ,truncate_table,mock_firebase):
    # Clear the table
    truncate_table("User")

    false_payload = {k : v for k,v in payload.items() }
    false_payload["tc"] = "1_000_000_000"
    
    # Perform user creation
    response = client.post("/register", json=false_payload)
    response_data = response.get_json()
    # logger.debug("Response Data:\n%s", json.dumps(response_data, indent=4))
    
    # Assert missing fields 
    assert response.status_code == 400, "Should return 400 bad request on validation error"
    assert "validation_error" in response_data, "Response should have validation_error"
    assert len(response_data["validation_error"]["body_params"]) == 1, "One false field needs to be detected"