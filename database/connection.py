from flask import current_app
import mysql.connector
from mysql.connector import Error

def get_db():
    try:
        connection = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            auth_plugin='mysql_native_password'
        )
        if connection.is_connected():
            return connection
        else:
            current_app.logger.error(f"Error: {err}")
            raise Exception("Failed to connect to the database.")
    except Error as err:
        current_app.logger.error(f"Error: {err}")
        raise Exception(f"Database connection failed: {err}")
    except Exception as err:
        current_app.logger.error(f"Unexpected error: {err}")
        raise Exception(f"Unexpected error: {err}")