import json
import logging
from unittest.mock import MagicMock
import tests.mock_data as mock_data
logger = logging.getLogger(__name__)

def test_usecase1_register_and_login(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    payload = {
        "email": mock_data.users[0]["Email"],
        "password": "securepassword",
        "name": mock_data.users[0]["Name"],
        "surname": mock_data.users[0]["Surname"],
        "tc": mock_data.users[0]["TC_ID"],
        "blood_type": mock_data.users[0]["Blood_Type"],
        "birth_date" : mock_data.users[0]["Birth_Date"]
    }
    # Perform user creation
    response = client.post("/register", json=payload)
    response_data = response.get_json()
    logger.info(response_data)
    # Assert user created successfully
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["message"] == "User created successfully"
    # token is used for login from here on
    
def test_usecase2_login_and_see_active_requests(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
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


def test_usecase3_create_request_for_someone_i_know(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
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
    # logged in user
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.post("/request", json=payload, headers=headers)
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data["message"] == "Request created and notification sent successfully."
    assert "request_id" in response_data
    assert "notification_id" in response_data
def test_usecase4_and_5_sees_the_requests_details_and_decides_to_donate(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", mock_data.users)
    insert_mock_data("Requests", mock_data.requests)
    headers = {"Authorization": mock_data.users[1]["User_id"]}
    response = client.get("/request/personalized", headers=headers)
    response_data = response.get_json()
    logger.info(response_data)

    assert response.status_code == 200
    assert response_data[0]["Blood_Type"] == mock_data.users[1]["Blood_Type"]
    
    headers = {"Authorization": mock_data.users[1]["User_id"]}
    payload = {"request_id" : response_data[0]["Request_ID"]}
    response = client.post("/on_the_way",json=payload, headers=headers)
    response_data = response.get_json()
    logger.info(response_data)
    assert response.status_code == 200
    
def test_usecase6_ineligble_donor_cant_donate(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    headers = {"Authorization": mock_data.users[2]["User_id"]}
    payload = {"request_id" : mock_data.requests[0]["Request_ID"]}
    response = client.post("/on_the_way",json=payload, headers=headers)
    assert response.status_code == 400
    headers = {"Authorization": mock_data.users[3]["User_id"]}
    payload = {"request_id" : mock_data.requests[0]["Request_ID"]}
    response = client.post("/on_the_way",json=payload, headers=headers)
    assert response.status_code == 200
def test_usecase7_approve_on_the_ways(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    response = client.get(f"/on_the_way/{mock_data.requests[0]['Request_ID']}")
    response_data = response.get_json()
    logger.info(response_data)
    assert response.status_code == 200

    payload = {
        'status' : 'completed'
    }
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.put(f"/on_the_way/{response_data[0]['Request_ID']}", json=payload, headers=headers)
    response_data = response.get_json()
    logger.info(response_data)

    assert response.status_code == 200
    headers = {"Authorization": mock_data.users[0]["User_id"]}
    response = client.put(f"/on_the_way/{response_data[1]['Request_ID']}", json=payload, headers=headers)
    response_data = response.get_json()
    logger.info(response_data)
    assert response.status_code == 200
    
    
    