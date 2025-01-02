from flask import current_app
import database.helper
def get_db():
    return database.helper.get_db_with_config(current_app.config)