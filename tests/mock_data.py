users = [
    {
        "User_id": "123123",
        "TC_ID": 12345678901,
        "City": "New York",
        "District": "Manhattan",
        "Birth_Date": "1990-01-01",
        "Name": "Alice",
        "Surname": "Smith",
        "Email": "alice@example.com",
        "Blood_Type": "0+",
        "Last_Donation_Date": "2023-01-01",
        "Is_Eligible": True
    },
    {
        "User_id": "1231234",
        "TC_ID": 12345678902,
        "City": "Los Angeles",
        "District": "Hollywood",
        "Birth_Date": "1995-05-05",
        "Name": "Bob",
        "Surname": "Johnson",
        "Email": "bob@example.com",
        "Blood_Type": "A-",
        "Last_Donation_Date": "2022-12-15",
        "Is_Eligible": True
    },
    {
        "User_id": "121212",
        "TC_ID": 12345678903,
        "City": "Los Angeles",
        "District": "Hollywood",
        "Birth_Date": "1995-05-05",
        "Name": "Bobby",
        "Surname": "Williamson",
        "Email": "bobby@example.com",
        "Blood_Type": "A-",
        "Last_Donation_Date": "2024-12-15",
        "Is_Eligible": False
    },
    {
        "User_id": "121212123123",
        "TC_ID": 12345678904,
        "City": "Los Angeles",
        "District": "Hollywood",
        "Birth_Date": "1995-05-05",
        "Name": "Bubba",
        "Surname": "Williamson",
        "Email": "Bubba@example.com",
        "Blood_Type": "A-",
        "Last_Donation_Date": "2023-01-01",
        "Is_Eligible": True
    },
]
requests = [
    {
        "Request_ID": 1,
        "Requested_TC_ID": users[0]["TC_ID"],
        "Patient_TC_ID": 98765432101,
        "Blood_Type": "A-",
        "Age": 30,
        "Gender": "Female",
        "Patient_Name": "Clara",
        "Patient_Surname": "Williams",
        "Status": "pending",
        "Donor_Count": 2,
        "City" : "Los Angeles",
        "District": "Manhattan"
    },
    {
        "Request_ID": 2,
        "Requested_TC_ID": users[1]["TC_ID"],
        "Patient_TC_ID": 98765432102,
        "Blood_Type": "B-",
        "Age": 40,
        "Gender": "Male",
        "Patient_Name": "David",
        "Patient_Surname": "Brown",
        "Status": "pending",
        "Donor_Count": 3,
        "City" : "Los Angeles",
        "District": "Manhattan"
    },
    {
        "Request_ID": 3,
        "Requested_TC_ID": users[1]["TC_ID"],
        "Patient_TC_ID": 98765432103,
        "Blood_Type": "0+",
        "Age": 40,
        "Gender": "Female",
        "Patient_Name": "Daviddd",
        "Patient_Surname": "Brownnnn",
        "Status": "pending",
        "Donor_Count": 7,
        "City" : "Los Angeles",
        "District": "Manhattan"
    },
]
ontheways = [
    {
        "Request_ID": requests[0]["Request_ID"],
        "Donor_TC_ID":users[1]["TC_ID"],
        "Status":"on_the_way",
    }
]