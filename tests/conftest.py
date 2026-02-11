import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tempfile
import sqlite3
import pytest
from werkzeug.security import generate_password_hash
from app import app, init_db
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# IMPORTANT: set env BEFORE importing app
os.environ["FLASK_ENV"] = "development"

from app import app, init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()

            conn = sqlite3.connect(app.config["DB_PATH"])
            cursor = conn.cursor()

            # Clean tables
            cursor.execute("DELETE FROM student")
            cursor.execute("DELETE FROM teacher")

            # Insert test student
            cursor.execute("""
                INSERT INTO student (
                    student_name, student_id, email, phone_number,
                    password, student_gender, student_dept
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Test Student",
                "S001",
                "student@test.com",
                "9999999999",
                generate_password_hash("password"),
                "F",
                "CSE"
            ))

            # Insert test teacher
            cursor.execute("""
                INSERT INTO teacher (
                    teacher_name, teacher_id, email, phone_number,
                    password, teacher_gender, teacher_dept
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Test Teacher",
                "T001",
                "teacher@test.com",
                "8888888888",
                generate_password_hash("password"),
                "M",
                "CSE"
            ))

            conn.commit()
            conn.close()

        yield client


    # os.close(db_fd)
    # os.unlink(db_path)
