from connection import get_db
import csv
import ast
import mysql.connector
from mysql.connector import Error
from flask import current_app
from settings_db import db_host, db_user, db_password, db_name

def get_db():
    try:
        connection = mysql.connector.connect(
            host= db_host,
            user= db_user,
            password= db_password,
            database= db_name,
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

try:
    cnx = get_db()
    cursor = cnx.cursor()


    def executeScriptsFromFile(filename):
        fd = open(filename, 'r')
        sqlFile = fd.read()
        fd.close()

        sqlCommands = sqlFile.split(';')

        for command in sqlCommands:
            try:
                if command.rstrip() != '':
                    cursor.execute(command)
            except ValueError as msg:
                print("Command skipped: ", msg)


    executeScriptsFromFile('./sql/schema.sql')
    cnx.commit()

except Exception as err:
    print("There was an error creating the database: ", err)
