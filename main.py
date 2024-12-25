from flask import Flask
from datetime import timedelta
import os
import firebase_admin
from firebase_admin import credentials
from flask_cors import CORS
from src.request import request_bp
from src.user import user_bp
from src.auth import auth_bp
from src.banned_user import banned_bp
from dotenv import load_dotenv
load_dotenv()


def load_configs(app):

    app.config['DEBUG'] = os.getenv("DEBUG", "True") == "True"
    app.config['PORT'] = int(os.getenv("PORT", 8080))
    app.config['MYSQL_HOST'] = os.getenv("DOCKER_MYSQL_HOST",os.getenv("MYSQL_HOST", "localhost"))
    app.config['MYSQL_USER'] = os.getenv("DOCKER_MYSQL_USER",os.getenv("MYSQL_USER", "root"))
    app.config['MYSQL_PASSWORD'] = os.getenv("DOCKER_MYSQL_PASSWORD",os.getenv("MYSQL_PASSWORD", "root"))
    app.config['MYSQL_DB'] = os.getenv("DOCKER_MYSQL_DB",os.getenv("MYSQL_DB", "kanver"))
    # Set a secret key. Ensure this is set securely in production (e.g., through an env var).
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_local_dev')
    # Firebase Admin SDK setup
    cred = credentials.Certificate("firebase-auth.json")
    firebase_admin.initialize_app(cred)
app = Flask(__name__)
CORS(app, support_credentials=True)
load_configs(app)

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.route("/")
def hello():
    return "<h1>Ege AWS ile server kurdum!!!</h1><a href='/users'>Get All Users Count</a>"


app.register_blueprint(request_bp, url_prefix='/')
app.register_blueprint(user_bp, url_prefix='/')
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(banned_bp, url_prefix='/')



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

