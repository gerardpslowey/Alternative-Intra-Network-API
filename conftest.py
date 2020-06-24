import pytest
from api import create_app

# Give each test the same app to test
# This allows the actually Firebase database to be tested
app_context =  create_app()[0]

# These fixtures are ran before tests and set up the environment for tests e.g. variables 

# API the tests can call (tests call the name of the function as the variable returned by the function)
@pytest.fixture
def app():
    yield app_context

# Tests use this client to make requets instead of starting the server
@pytest.fixture
def client(app):
    return app.test_client()
