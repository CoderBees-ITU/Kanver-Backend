from connection import get_db
import csv
import ast

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


    executeScriptsFromFile('./database/schema.sql')
    cnx.commit()

except Exception as err:
    print("There was an error creating the database: ", err)
