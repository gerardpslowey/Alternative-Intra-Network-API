import os, requests

import pytest

from api import create_app

global address

global API

app_context =  create_app()[0]

@pytest.fixture
def app():
    yield app_context


@pytest.fixture
def client(app):
    return app.test_client()
