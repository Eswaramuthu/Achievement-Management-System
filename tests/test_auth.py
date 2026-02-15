# tests/test_auth.py
def test_student_login_success(client, test_db):
    """Test successful student login."""
    # First get the login page to ensure session is set up
    login_page = client.get('/student')
    assert login_page.status_code == 200
    
    # Now post the login data
    response = client.post('/student', data={
        'sname': 'S001',
        'password': 'password',
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check for dashboard content or redirect
    assert b"Student" in response.data

def test_student_login_failure(client, test_db):
    """Test failed student login."""
    login_page = client.get('/student')
    assert login_page.status_code == 200
    
    response = client.post('/student', data={
        'sname': 'S001',
        'password': 'wrongpassword',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid" in response.data

def test_teacher_login_success(client, test_db):
    """Test successful teacher login."""
    login_page = client.get('/teacher')
    assert login_page.status_code == 200
    
    response = client.post('/teacher', data={
        'tname': 'T001',
        'password': 'password',
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Teacher" in response.data