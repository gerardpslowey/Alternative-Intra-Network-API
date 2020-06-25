import pytest
import requests
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
    # Make test device here
    return app.test_client()

def test_device_id(client, app):
    client.post("/api/3FJwnCg-fHhcwQP3c59u_w/devices?id=test", data={"deviceName":"test", "gatewayController":"192.168.0.132", "volumeAvailable":10})
    return "test_device_id"
