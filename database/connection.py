from flask import current_app
import mysql.connector
from mysql.connector import Error
def get_db(config=None):
    try:
        if config is None:
            config = {
                'MYSQL_PORT': current_app.config['MYSQL_PORT'],
                'MYSQL_HOST': current_app.config['MYSQL_HOST'],
                'MYSQL_USER': current_app.config['MYSQL_USER'],
                'MYSQL_PASSWORD': current_app.config['MYSQL_PASSWORD'],
                'MYSQL_DB': current_app.config['MYSQL_DB'],
            }
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