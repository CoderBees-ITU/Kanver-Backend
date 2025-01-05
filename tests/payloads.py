users = [
    {
        "User_id": "123123",
        "TC_ID": 12345678901,
        "Name": "Alice",
        "Surname": "Smith",
        "Email": "alice@example.com",
        "Birth_Date": "1990-01-01",
        "Is_Eligible": True
    },
    {
        "User_id": "1231234",
        "TC_ID": 12345678902,
        "Name": "Bob",
        "Surname": "Johnson",
        "Email": "bob@example.com",
        "Birth_Date": "1995-05-05",
        "Is_Eligible": True
    }
]
requests = [
    {
        "Request_ID": 1,
        "Requested_TC_ID": users[0]["TC_ID"],
        "Patient_TC_ID": 98765432101,
        "Blood_Type": "A+",
        "Age": 30,
        "Gender": "Female",
        "Patient_Name": "Clara",
        "Patient_Surname": "Williams",
        "Status": "pending",
        "Donor_Count": 2
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
        "Donor_Count": 3
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
        "Donor_Count": 7
    }
]
ontheways = [
    {
        "Request_ID": requests[0]["Request_ID"],
        "Donor_TC_ID":users[0]["TC_ID"],
        "Status":"on_the_way",
    }
]