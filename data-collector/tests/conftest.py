import pytest
import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
from src.app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client():
    return flask_app.test_client()