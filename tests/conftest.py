import os
import tempfile

import pytest
from flaskr import create_app

@pytest.fixture
def app():
    db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True
    })

    with app.app_context():
    	pass

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()