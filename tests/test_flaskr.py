import os
import tempfile

import pytest

from app_server import app_server

@pytest.fixture
def client():
    flaskr.app.config['TESTING'] = True

    with flaskr.app.test_client() as client:
        with flaskr.app.app_context():
        	pass