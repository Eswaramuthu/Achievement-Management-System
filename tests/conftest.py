# tests/conftest.py

import os
import tempfile
import sqlite3
import pytest
from app import app
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="session")
def test_app():
    """Create and configure a test instance of the app."""

    # Create isolated temporary database
    db_fd, db_path = tempfile.mkstemp()

    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "DATABASE": db_path,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SECRET_KEY": "test-secret-key",
    })

    # Mock CSRF token for templates
    app.jinja_env.globals["csrf_token"] = lambda: "test-token"

    with app.app_context():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ===============================
        # Create Tables
        # ===============================

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS student (
                student_name TEXT NOT NULL,
                student_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                password TEXT NOT NULL,
                student_gender TEXT,
                student_dept TEXT
            );

            CREATE TABLE IF NOT EXISTS teacher (
                teacher_name TEXT NOT NULL,
                teacher_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                password TEXT NOT NULL,
                teacher_gender TEXT,
                teacher_dept TEXT
            );
        """)

        # ===============================
        # Insert Test Data
        # ===============================

        cursor.execute("""
            INSERT OR REPLACE INTO student VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Test Student",
            "S001",
            "student@test.com",
            "1234567890",
            generate_password_hash("password"),
            "M",
            "CSE"
        ))

        cursor.execute("""
            INSERT OR REPLACE INTO teacher VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Test Teacher",
            "T001",
            "teacher@test.com",
            "0987654321",
            generate_password_hash("password"),
            "F",
            "CSE"
        ))

        conn.commit()
        conn.close()

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_app):
    """Flask test client."""
    return test_app.test_client()


@pytest.fixture
def auth_student_client(client):
    """Authenticated student client."""
    with client.session_transaction() as sess:
        sess.update({
            "logged_in": True,
            "student_id": "S001",
            "student_name": "Test Student",
            "student_dept": "CSE",
        })
    return client


@pytest.fixture
def auth_teacher_client(client):
    """Authenticated teacher client."""
    with client.session_transaction() as sess:
        sess.update({
            "logged_in": True,
            "teacher_id": "T001",
            "teacher_name": "Test Teacher",
            "teacher_dept": "CSE",
        })
    return client


@pytest.fixture
def test_db(test_app):
    """Provide database connection for tests."""
    with test_app.app_context():
        conn = sqlite3.connect(test_app.config["DATABASE"])
        yield conn
        conn.close()
