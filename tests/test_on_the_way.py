import json
import logging
from unittest.mock import MagicMock
import tests.payloads as payloads
logger = logging.getLogger(__name__)

def test_add_on_the_way_valid(client, db_connection, truncate_table, insert_mock_data,mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    # Simulate valid request
    payload = {"request_id": payloads.requests[0]['Request_ID']}
    headers = {"Authorization": payloads.users[0]['User_id']}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['message'] == "Donor successfully marked as on the way."

def test_add_on_the_way_missing_request_id(client):
    payload = {}
    headers = {"Authorization": "test_user"}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "InvalidInput"
    assert "Request ID and valid User_ID are required." in response_data['message']
def test_add_on_the_way_missing_authorization(client):
    payload = {"request_id": 1}
    response = client.post("/on_the_way", json=payload)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "InvalidInput"
    assert "Request ID and valid User_ID are required." in response_data['message']
def test_add_on_the_way_user_not_found(client, truncate_table):
    truncate_table("User")

    payload = {"request_id": 1}
    headers = {"Authorization": "non_existent_user"}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "InvalidInput"
    assert "user_id of requester is not found in the database." in response_data['message']
def test_add_on_the_way_already_exists(client, db_connection, insert_mock_data,truncate_table):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)

    payload = {"request_id": payloads.ontheways[0]["Request_ID"]}
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "InvalidOnTheWay"
    assert "This Donor TC ID was already used for this blood request" in response_data['message']
def test_add_on_the_way_not_eligible(client, db_connection, insert_mock_data, truncate_table):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    
    cursor = db_connection.cursor()
    cursor.execute("""
                   UPDATE User SET Is_Eligible = false WHERE User_id = %s""", (payloads.users[0]["User_id"],))
    db_connection.commit()
    payload = {"request_id": payloads.requests[0]["Request_ID"]}
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "NotEligible"
    assert "Donor is not eligible to donate blood." in response_data['message']
def test_add_on_the_way_request_closed(client, db_connection, insert_mock_data,truncate_table):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    
    cursor = db_connection.cursor()
    cursor.execute("""
                   UPDATE Requests SET status = %s WHERE Request_ID = %s""", ("closed",payloads.requests[0]["Request_ID"],))
    db_connection.commit()
    payload = {"request_id": payloads.requests[0]["Request_ID"]}
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "RequestClosed"
    assert "This blood request is no longer open." in response_data['message']


def test_add_on_the_way_invalid_user(client, db_connection, truncate_table, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")

    payload = {"request_id": 1}
    headers = {"Authorization": "non_existing_user"}
    response = client.post("/on_the_way", json=payload, headers=headers)
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data['error'] == "InvalidInput"




def test_cancel_on_the_way(client, db_connection, truncate_table,insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)


    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.delete(f"/on_the_way/{payloads.ontheways[0]["Request_ID"]}", headers=headers)
    response_data = response.get_json()

    assert response.status_code == 200
    assert response_data['message'] == "Donor successfully removed from on-the-way status."

def test_cancel_on_the_way_missing_auth(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)
    
    # Make DELETE request without Authorization header
    response = client.delete(f"/on_the_way/{payloads.ontheways[0]["Request_ID"]}")
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 400
    assert response_data['error'] == "InvalidInput"
    assert "user_id of requester is not found in the database." in response_data['message']

def test_cancel_on_the_way_user_not_found(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)

    # Make DELETE request with non-existent user
    headers = {"Authorization": "non_existent_user"}
    response = client.delete(f"/on_the_way/{payloads.ontheways[0]["Request_ID"]}", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 400
    assert response_data['error'] == "InvalidInput"
    assert "user_id of requester is not found in the database." in response_data['message']

def test_cancel_on_the_way_no_record(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)
    # No matching record in On_The_Way table
    invalid_on_the_way_id = 99999999
    # Make DELETE request
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.delete(f"/on_the_way/{invalid_on_the_way_id}", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 404
    assert response_data['error'] == "NotFound"
    assert "No matching record found for this donor and request." in response_data['message']


def test_update_on_the_way_status_success(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)

    # Make DELETE request
    headers = {"Authorization": payloads.users[0]["User_id"]}
    payload = {"status": "Donated"}
    response = client.put(f"/on_the_way/{payloads.ontheways[0]["Request_ID"]}", json=payload, headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert response_data["message"] == "Status updated successfully."


def test_update_on_the_way_status_missing_status(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)
    insert_mock_data("On_The_Way", payloads.ontheways)

    # Make PUT request with missing status
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.put(f"/on_the_way/{payloads.ontheways[0]["Request_ID"]}", json={}, headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 400
    assert response_data["error"] == "InvalidInput"
    assert "Status is required." in response_data["message"]
