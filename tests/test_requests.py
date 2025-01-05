import json
import logging
from unittest.mock import MagicMock
import tests.payloads as payloads
logger = logging.getLogger(__name__)
from urllib.parse import quote
def test_get_requests_all(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)

    # Make GET request
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.get("/request", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(payloads.requests)  # Two requests in mock data
    assert response_data[0]["Request_ID"] == payloads.requests[0]["Request_ID"]
    assert response_data[1]["Request_ID"] == payloads.requests[1]["Request_ID"]

def test_get_requests_filter_blood_type(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)

    # Make GET request with blood type filter
    blood_type = "0+"
    headers = {"Authorization": payloads.users[0]["User_id"]}
    response = client.get(f"/request?blood_type={quote(blood_type)}", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(list(filter(lambda x : x["Blood_Type"] == blood_type ,payloads.requests)))  
    assert response_data[0]["Blood_Type"] == "0+"

def test_get_my_requests(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)

    # GET my requests 
    user = payloads.users[0]
    headers = {"Authorization": user["User_id"]}
    response = client.get(f"/request/my_requests", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(list(filter(lambda x : x["Requested_TC_ID"] == user["TC_ID"] ,payloads.requests)))  
    assert response_data[0]["Requested_TC_ID"] == user["TC_ID"]
def test_get_personalized_requests(client, db_connection, truncate_table, insert_mock_data, mock_firebase):
    truncate_table("User")
    truncate_table("Requests")
    truncate_table("On_The_Way")
    insert_mock_data("User", payloads.users)
    insert_mock_data("Requests", payloads.requests)

    # Get personalized request recommendations
    user = payloads.users[0]
    headers = {"Authorization": user["User_id"]}
    response = client.get(f"/request/personalized", headers=headers)
    response_data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert len(response_data) == len(list(filter(
            lambda x : 
                x["Requested_TC_ID"] != user["TC_ID"]            ,payloads.requests)))  
    assert response_data[0]["Requested_TC_ID"] != user["TC_ID"]