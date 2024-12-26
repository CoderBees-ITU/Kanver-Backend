# Testing the `/register` API

This testing setup includes test cases for the `/register` API (for now) to ensure proper functionality and error handling.

---

## **Setup and Running Tests**

### 1. Build and Start the Test Environment
Run the following command to build and start the services required for testing:

```bash
docker-compose -f docker-compose.test.yml up --build
```

## Test Coverage

The current test suite covers the following scenarios for the `/register` API:

### Successful User Registration:
    A new user is successfully created with valid input data.
### User Already Exists:
    Tests the scenario where a user with the same email or tc_id already exists in the database.
### Missing Required Fields:
    Tests for missing fields such as email, password, or tc_id, ensuring proper error handling.
### Validation Errors:
    Tests invalid input data formats (e.g., invalid email format or non-numeric tc_id).

## Test Utilities

The following utilities are included in the test setup:

### Fixtures:
`db_connection`: Provides a connection to the test database.

`truncate_table`: Utility to clear specific tables before a test.

`mock_firebase`: Mock Firebase functions to simulate user creation, deletion, token creation and verification without interacting with a real Firebase instance.


### UserRegister Test Payload: The test payload is used to simulate valid and invalid input data for the /register API.
