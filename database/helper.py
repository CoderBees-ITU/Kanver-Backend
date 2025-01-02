import mysql.connector
from mysql.connector import Error

def get_db_with_config(config):
    try:
        connection = mysql.connector.connect(
            port=config['MYSQL_PORT'],
            host=config['MYSQL_HOST'],
            user=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            database=config['MYSQL_DB'],
            auth_plugin='mysql_native_password'
        )
        if connection.is_connected():
            return connection
        else:
            raise Exception("Failed to connect to the database.")
    except Error as err:
        raise Exception(f"Database connection failed: {err}")
    except Exception as err:
        raise Exception(f"Unexpected error: {err}")