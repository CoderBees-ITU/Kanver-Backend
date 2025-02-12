# Firebase Related Fixtures
import logging
from unittest.mock import MagicMock

import pytest
from firebase_admin import auth

logger = logging.getLogger(__name__)

# Define your mock functions
def delete_user(uid):
    if uid == "test_user_id":
        pass
    else:
        raise ValueError("Invalid user uid is used for deleting")

def create_user(email, password, display_name):
    mock_user_record = MagicMock()
    mock_user_record.uid = "test_user_id"
    mock_user_record.email = email
    return mock_user_record

def create_custom_token(uid):
    if uid == "test_user_id":
        return b"mock_token"
    else:
        raise ValueError("Invalid user uid is used for custom token")

def verify_id_token(token):
    if token == "mock_token":
        return {
            "uid": "test_user_id",
            "email": "test@example.com"   
        }
    else:
        raise auth.InvalidIdTokenError("Invalid token")

# Define a pytest fixture to mock Firebase
@pytest.fixture
def mock_firebase(monkeypatch):
    mock_verify_id_token = MagicMock(side_effect=verify_id_token)
    mock_delete_user = MagicMock(side_effect=delete_user)
    mock_create_user = MagicMock(side_effect=create_user)
    mock_create_custom_token = MagicMock(side_effect=create_custom_token)

    # Apply monkeypatches
    monkeypatch.setattr("firebase_admin.auth.delete_user", mock_delete_user)
    monkeypatch.setattr("firebase_admin.auth.create_user", mock_create_user)
    monkeypatch.setattr("firebase_admin.auth.create_custom_token", mock_create_custom_token)
    monkeypatch.setattr("firebase_admin.auth.verify_id_token", mock_verify_id_token)


#  Database related fixtures
import pytest
import os
from database.helper import get_db_with_config
from mysql.connector.cursor import MySQLCursorDict
def get_configs():
    config = {}
    config['MYSQL_PORT'] = int(os.getenv("DOCKER_MYSQL_PORT",os.getenv("MYSQL_PORT", "3306")))
    config['MYSQL_HOST'] = os.getenv("DOCKER_MYSQL_HOST",os.getenv("MYSQL_HOST", "localhost"))
    config['MYSQL_USER'] = os.getenv("DOCKER_MYSQL_USER",os.getenv("MYSQL_USER", "root"))
    config['MYSQL_PASSWORD'] = os.getenv("DOCKER_MYSQL_PASSWORD",os.getenv("MYSQL_PASSWORD", "root"))
    config['MYSQL_DB'] = os.getenv("DOCKER_MYSQL_DB",os.getenv("MYSQL_DB", "kanver"))
    return config

@pytest.fixture(scope="session")
def db_config():
    """
    Provide the database configuration for tests.
    """
    return get_configs()

@pytest.fixture
def db_connection(db_config):
    """
    Provide a database connection for tests.
    """
    connection = get_db_with_config(db_config)
    connection.cursor_class = MySQLCursorDict  # Set cursor to return dictionaries
    yield connection
    connection.close()

@pytest.fixture
def truncate_table(db_connection):
    """
    Truncate the table in the database.
    """
    def truncate_table_wrapper(table):
        cursor = db_connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # Disable foreign key checks
        cursor.execute(f"TRUNCATE TABLE {table};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # Re-enable foreign key checks
        db_connection.commit()
        cursor.close()
    return truncate_table_wrapper

@pytest.fixture
def insert_mock_data(db_connection):
    """
    Insert mock data and return the inserted data.
    """
    def insert_mock_data_wrapper(table, data):
        """
        Inserts the provided data into the specified table.
        Args:
            table (str): The name of the table to insert data into.
            data (list[dict]): A list of dictionaries where each dictionary represents a row.
        Returns:
            list[dict]: The inserted data.
        """
        if not data:
            raise ValueError("Data cannot be empty.")

        # Extract column names from the first dictionary
        columns = data[0].keys()

        # Create SQL query dynamically
        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

        # Insert all rows
        cursor = db_connection.cursor()
        values = [tuple(row[col] for col in columns) for row in data]
        cursor.executemany(query, values)
        db_connection.commit()
    return insert_mock_data_wrapper
