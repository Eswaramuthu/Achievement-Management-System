# tests/conftest.py
import os
import tempfile
import pytest
from app import app, init_db
from werkzeug.security import generate_password_hash
import sqlite3

@pytest.fixture(scope='session')
def test_app():
    """Create and configure a new app instance for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'DATABASE': db_path,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
    })
    app.jinja_env.globals['csrf_token'] = lambda: 'test-token'


    # Create the test database and tables
    with app.app_context():
        # Initialize the database (this should create the tables)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables manually since we're in test mode
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            student_name TEXT NOT NULL,
            student_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            student_gender TEXT,
            student_dept TEXT
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher (
            teacher_name TEXT NOT NULL,
            teacher_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            password TEXT NOT NULL,
            teacher_gender TEXT,
            teacher_dept TEXT
        )''')
        
        # Add test data
        cursor.execute("""
            INSERT OR REPLACE INTO student (
                student_name, student_id, email, phone_number, 
                password, student_gender, student_dept
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'Test Student', 'S001', 'student@test.com', '1234567890',
            generate_password_hash('password'), 'M', 'CSE'
        ))
        
        cursor.execute("""
            INSERT OR REPLACE INTO teacher (
                teacher_name, teacher_id, email, phone_number,
                password, teacher_gender, teacher_dept
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'Test Teacher', 'T001', 'teacher@test.com', '0987654321',
            generate_password_hash('password'), 'F', 'CSE'
        ))
        
        conn.commit()
        conn.close()
    
    yield app

    # Clean up the test database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture
def auth_student_client(client):
    """Return a client with student logged in."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['student_id'] = 'S001'
        sess['student_name'] = 'Test Student'
        sess['student_dept'] = 'CSE'
    return client

@pytest.fixture
def auth_teacher_client(client):
    """Return a client with teacher logged in."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['teacher_id'] = 'T001'
        sess['teacher_name'] = 'Test Teacher'
        sess['teacher_dept'] = 'CSE'
    return client

# Add this fixture for test_db to be used in test files
@pytest.fixture
def test_db(test_app):
    """Fixture to ensure the test database is set up."""
    with test_app.app_context():
        conn = sqlite3.connect(test_app.config['DATABASE'])
        yield conn
        conn.close()
        