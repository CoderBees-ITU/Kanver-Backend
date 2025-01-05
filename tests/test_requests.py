import json
import logging
from unittest.mock import MagicMock
import tests.mock_data as mock_data
logger = logging.getLogger(__name__)
from urllib.parse import quote
def test_get_requests_all(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # Make GET request
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.get("/request", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(mock_data.requests)  # Two requests in mock data
    assert response_data[0]["Request_ID"] == mock_data.requests[0]["Request_ID"]
    assert response_data[1]["Request_ID"] == mock_data.requests[1]["Request_ID"]

def test_get_requests_filter_blood_type(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # Make GET request with blood type filter
    blood_type = "0+"
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.get(f"/request?blood_type={quote(blood_type)}", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(list(filter(lambda x : x["Blood_Type"] == blood_type ,mock_data.requests)))  
    assert response_data[0]["Blood_Type"] == "0+"

def test_get_my_requests(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # GET my requests 
    user = mock_data.users[0]
    headers = {"Authorization": user["User_id"]}
    response = client.get(f"/request/my_requests", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(list(filter(lambda x : x["Requested_TC_ID"] == user["TC_ID"] ,mock_data.requests)))  
    assert response_data[0]["Requested_TC_ID"] == user["TC_ID"]
def test_get_personalized_requests(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # Get personalized request recommendations
    user = mock_data.users[0]
    headers = {"Authorization": user["User_id"]}
    response = client.get(f"/request/personalized", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(list(filter(
            lambda x : 
                x["Requested_TC_ID"] != user["TC_ID"]            ,mock_data.requests)))  
    assert response_data[0]["Requested_TC_ID"] != user["TC_ID"]

def test_create_request_success_for_me(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    insert_mock_data("User", mock_data.users)
    payload = {
    "patient_tc_id": 98765432101,
    "blood_type": "0+",
    "age": 45,
    "gender": "Male",
    "note": "Urgent need for surgery.",
    "patient_name": "John",
    "patient_surname": "Smith",
    "location" : {
        "lat": 40.712776,
        "lng": -74.005974,
        "city": "New York",
        "district": "Manhattan",
    },
    "hospital": "General Hospital",
    "donor_count": 5,
    "status": "pending"
}


    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.post("/request", json=payload, headers=headers)
    response_data = response.get_json()
    # logger.info(response_data)
    # Assertions
    assert response.status_code == 200
    assert response_data["message"] == "Request created and notification sent successfully."
    assert "request_id" in response_data
    assert "notification_id" in response_data
def test_create_request_success_for_someone_i_know(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    insert_mock_data("User", mock_data.users)
    payload = {
    "patient_tc_id": "",
    "blood_type": "",
    "age": 0,
    "gender": "Male",
    "note": "Urgent need for surgery.",
    "location" : {
        "lat": 40.712776,
        "lng": -74.005974,
        "city": "New York",
        "district": "Manhattan",
    },
    "hospital": "General Hospital",
    "donor_count": 5,
    "status": "pending"
    }

    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.post("/request", json=payload, headers=headers)
    response_data = response.get_json()
    # logger.info(response_data)
    # Assertions
    assert response.status_code == 200
    assert response_data["message"] == "Request created and notification sent successfully."
    assert "request_id" in response_data
    assert "notification_id" in response_data

# def test_update_request_success(client, db_connection, truncate_table, insert_mock_data):
#     truncate_table("User")
#     truncate_table("Requests")
#     insert_mock_data("User", mock_data.users)
#     insert_mock_data("Requests", mock_data.requests)
#     # Define payload
#     payload = {
#         "request_id": 1,
#         "donor_count": 10,
#         "location": {"city": "New York", "district": "Manhattan"},
#         "hospital": "Updated Hospital",
#         "status": "closed",
#         "gender": "Female",
#         "note": "Updated note for request."
#     }

#     headers = {"Authorization": mock_data.users[0]["User_id"]}
#     response = client.put("/request", json=payload, headers=headers)
#     response_data = response.get_json()

#     # Assertions
#     assert response.status_code == 200
#     assert response_data["message"] == "Request updated successfully."

def test_delete_request_success(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # Make DELETE request
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.delete(f"/request?request_id={mock_data.requests[0]['Request_ID']}", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert response_data["message"] == "Request deleted successfully."
def test_delete_request_missing_request_id(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # Make DELETE request without request_id
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.delete("/request", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 400
    assert response_data["error"] == "InvalidInput"
    assert response_data["message"] == "Request ID is required."
    
def test_delete_request_unauthorized_user(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)

    # Make DELETE request with different user id
    headers = {"Authorization": mock_data.users[1]["User_id"]}
    response = client.delete(f"/request?request_id={mock_data.requests[0]['Request_ID']}", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 403
    assert response_data["error"] == "Unauthorized"
    assert response_data["message"] == "You are not authorized to delete this request."

