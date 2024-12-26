import pytest
from main import app as server_app
from tests.fixtures import *  # all fixtures from fixtures.py

@pytest.fixture
def app():
    yield server_app
@pytest.fixture
def client(app):
    return app.test_client()