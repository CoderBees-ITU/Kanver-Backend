import random
from locust import HttpUser, task, between, events
from database.helper import get_db_with_config
# Predefined list of user IDs
# Function to fetch the max TC_ID from the database

payload = {
        "email": "test@example.com",
        "password": "securepassword",
        "name": "Test",
        "surname": "User",
        "tc": "12345678901",
        "blood_type": "0+",
        "birth_date" : "1992-03-15"
}
valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-']
random_names = [
    "Alice", "Bob", "Charlie", "David", "Emily", 
    "Fiona", "George", "Hannah", "Isaac", "Julia", 
    "Kevin", "Laura", "Michael", "Nina", "Oliver", 
    "Peter", "Quinn", "Rachel", "Sophia", "Thomas", 
    "Ursula", "Victor", "Wendy", "Xander", "Yvonne", "Zachary"
]
random_surnames = [
    "Smith", "Johnson", "Brown", "Williams", "Jones", 
    "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", 
    "Lee", "Perez", "Thompson", "White", "Harris", 
    "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]
import os
config = {}
config["MYSQL_PORT"] = int(os.getenv("DOCKER_MYSQL_PORT",os.getenv("MYSQL_PORT", "3306")))
config["MYSQL_HOST"] = os.getenv("DOCKER_MYSQL_HOST",os.getenv("MYSQL_HOST", "localhost"))
config["MYSQL_USER"] = os.getenv("DOCKER_MYSQL_USER",os.getenv("MYSQL_USER", "root"))
config["MYSQL_PASSWORD"] = os.getenv("DOCKER_MYSQL_PASSWORD",os.getenv("MYSQL_PASSWORD", "root"))
config["MYSQL_DB"] = os.getenv("DOCKER_MYSQL_DB",os.getenv("MYSQL_DB", "kanver"))
config["DOCKER_BACKEND_HOST"] = os.getenv("DOCKER_BACKEND_HOST", "http://localhost:8080")
class SpawnedUser(HttpUser):
    # Simulate users waiting between requests
    wait_time = between(1, 5)
    host = config["DOCKER_BACKEND_HOST"]
    def on_start(self):
        """
        Runs when a user is spawned.
        Assign a unique ID to each user.
        """
        self.tc = random.randint(10**10 + 1, 10**11 - 1 )
        temp_payload = payload.copy()
        temp_payload["tc"] = self.tc
        temp_payload["name"] = random.choice(random_names)
        temp_payload["surname"] = random.choice(random_surnames)
        temp_email = temp_payload["email"].split("@")
        temp_payload["email"] = f"{temp_email[0]}_{temp_payload['name'] + temp_payload['surname']}_{self.tc}@{temp_email[1]}"
        temp_payload["blood_type"] = random.choice(valid_blood_types)
        self.payload = temp_payload
        self.client.post("/register", json=self.payload)
        db = get_db_with_config(config=config)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM User WHERE TC_ID = %s", (self.payload["tc"],))
        user = cursor.fetchone()
        db.close()
        cursor.close()
        if not user:
            self.stop()
            return
        self.user_id = user[0]
    def stop(self):
        """
        Stops this user and triggers Locust's stop logic.
        """
        events.request.fire(
            request_type="STOP",
            name="User spawn check",
            response_time=0,
            response_length=0,
            exception=f"Duplicate TC_ID: {self.tc}",
        )
        super().stop()
    @task(3)
    def get_requests(self):
        """
        Simulates a GET request to the /request endpoint.
        """
        headers = {"Authorization": self.user_id}
        self.client.get("/request", headers=headers)


    @task(1)
    def post_request(self):
        """
        Simulates a POST request to the /request endpoint.
        """
        payload = {
            "donor_count": random.randint(1, 5),
            "location": {"city": "Test City", "district": "Test District", "lat": 40.7128, "lng": -74.0060},
            "hospital": "Test Hospital",
            "status": "pending",
            "gender": "Male",
            "blood_type": random.choice(valid_blood_types),
            "age": random.randint(18, 65),
            "patient_name": f"Patient_{random.randint(1, 100)}",
            "patient_surname": f"Surname_{random.randint(1, 100)}"
        }
        headers = {"Authorization": self.user_id}
        self.client.post("/request", json=payload, headers=headers)

