
import os
import sys
import tempfile
import pytest
from flask import Flask

# Add the application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as app_module
from app import app, init_db

@pytest.fixture
def client():
    # Create a temporary file to use as the database
    db_fd, db_path = tempfile.mkstemp()
    
    # Set the DB_PATH for the test environment
    app.config['DB_PATH'] = db_path
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    # Patch the global DB_PATH in app module
    old_db_path = app_module.DB_PATH
    app_module.DB_PATH = db_path

    # Initialize the database
    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client

    # Restore DB_PATH (though not strictly necessary as process will exit)
    app_module.DB_PATH = old_db_path

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)
