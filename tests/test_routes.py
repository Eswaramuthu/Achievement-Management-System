
import pytest

def test_protected_route_access_denied(client):
    """Test accessing protected route without login."""
    response = client.get("/student-dashboard", follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200
    # Check for login page content
    assert b"Login" in response.data or b"student" in response.data

def test_protected_route_access_granted(client):
    """Test accessing protected route after login."""
    # Register and Login first
    client.post("/student_new", data={
        "student_name": "Protected User",
        "student_id": "P123",
        "email": "protected@test.com",
        "phone_number": "1234567890",
        "password": "password123",
        "student_gender": "F",
        "student_dept": "ECE"
    }, follow_redirects=True)

    client.post("/student", data={
        "sname": "P123",
        "password": "password123"
    }, follow_redirects=True)

    # Access protected dashboard
    response = client.get("/student-dashboard")
    
    assert response.status_code == 200
    assert b"Student Dashboard" in response.data
