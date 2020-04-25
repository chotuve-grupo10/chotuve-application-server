import os
import tempfile

import pytest
from app_server import create_app

@pytest.fixture
def app():
    db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True
    })

    with app.app_context():
    	pass

    return app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()