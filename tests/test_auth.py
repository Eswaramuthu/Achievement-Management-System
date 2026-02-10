
import pytest
from app import app

def test_student_registration(client):
    """Test student registration."""
    # Use /student_new as identified in app.py
    response = client.post("/student_new", data={
        "student_name": "New Student",
        "student_id": "S123",
        "email": "newstudent@test.com",
        "phone_number": "1234567890",
        "password": "password123",
        "student_gender": "M",
        "student_dept": "CSE"
    }, follow_redirects=True)
    
    # Check if registration was successful (redirects to login page)
    assert response.status_code == 200
    # The registration redirects to 'student' route which renders student.html
    # We can check for "Student Login" or similar text present in student.html
    # Based on analyzing app.py, it redirects to url_for("student")
    assert b"student" in response.data or b"Login" in response.data

def test_login_success(client):
    """Test successful login."""
    # First, register a student
    client.post("/student_new", data={
        "student_name": "Login User",
        "student_id": "L123",
        "email": "login@test.com",
        "phone_number": "1234567890",
        "password": "password123",
        "student_gender": "M",
        "student_dept": "CSE"
    }, follow_redirects=True)

    # Now try to login
    response = client.post("/student", data={
        "sname": "L123",  # Note: app.py uses 'sname' for student_id in login form
        "password": "password123"
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check for dashboard content
    # student_dashboard.html contains "Student Dashboard"
    assert b"Student Dashboard" in response.data

def test_login_failure(client):
    """Test login with invalid credentials."""
    response = client.post("/student", data={
        "sname": "NONEXISTENT",
        "password": "wrongpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check for error message
    assert b"Invalid credentials" in response.data
