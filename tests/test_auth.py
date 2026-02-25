# tests/test_auth.py

import pytest


# =====================================================
# 🔐 Student Login Tests
# =====================================================

def test_student_login_success(client, test_db):
    """Ensure student can log in with correct credentials."""

    # Load login page
    response = client.get("/student")
    assert response.status_code == 200

    # Submit valid credentials
    response = client.post(
        "/student",
        data={
            "sname": "S001",
            "password": "password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Student" in response.data


def test_student_login_failure(client, test_db):
    """Ensure student login fails with incorrect password."""

    response = client.get("/student")
    assert response.status_code == 200

    response = client.post(
        "/student",
        data={
            "sname": "S001",
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid" in response.data


# =====================================================
# 👩‍🏫 Teacher Login Tests
# =====================================================

def test_teacher_login_success(client, test_db):
    """Ensure teacher can log in with correct credentials."""

    response = client.get("/teacher")
    assert response.status_code == 200

    response = client.post(
        "/teacher",
        data={
            "tname": "T001",
            "password": "password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Teacher" in response.data
