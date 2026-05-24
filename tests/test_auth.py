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


def test_student_registration_weak_password(client, test_db):
    """Weak passwords must fail registration."""
    response = client.post('/student_new', data={
        'student_name': 'Weak Password',
        'student_id': 'S002',
        'email': 'weak@test.com',
        'phone_number': '9876543210',
        'password': 'weakpass',
        'student_gender': 'Male',
        'student_dept': 'CSE'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password is too weak" in response.data


def test_student_registration_invalid_mobile(client, test_db):
    """Invalid mobile numbers should show a validation error."""
    response = client.post('/student_new', data={
        'student_name': 'Invalid Phone',
        'student_id': 'S003',
        'email': 'phone@test.com',
        'phone_number': '12345abcde',
        'password': 'Strong@123',
        'student_gender': 'Female',
        'student_dept': 'ECE'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Mobile number must contain exactly 10 digits" in response.data


def test_student_registration_success_redirects_to_login(client, test_db):
    """Successful registration should redirect the user to login with a success message."""
    response = client.post('/student_new', data={
        'student_name': 'Valid Student',
        'student_id': 'S004',
        'email': 'valid@test.com',
        'phone_number': '9876543210',
        'password': 'Karthik@123',
        'student_gender': 'Other',
        'student_dept': 'MECH'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Registration submitted! Your account will be activated after admin approval." in response.data