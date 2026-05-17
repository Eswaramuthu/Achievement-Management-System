# tests/test_protected_routes.py
def test_student_dashboard_protected(client):
    """Test that student dashboard requires authentication."""
    response = client.get('/student-dashboard', follow_redirects=False)
    assert response.status_code == 302  # Should redirect to login
    assert '/student' in response.location

def test_teacher_dashboard_protected(client):
    """Test that teacher dashboard requires authentication."""
    response = client.get('/teacher-dashboard', follow_redirects=False)
    assert response.status_code == 302  # Should redirect to login
    assert '/teacher' in response.location

def test_authenticated_student_access(client):
    """Test that authenticated student can access their dashboard."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['student_id'] = 'S12345'
        sess['student_name'] = 'Test Student'
        sess['student_dept'] = 'CSE'

    response = client.get('/student-dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Student Dashboard' in response.data

def test_authenticated_teacher_access(client):
    """Test that authenticated teacher can access their dashboard."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['teacher_id'] = 'T001'
        sess['teacher_name'] = 'Test Teacher'
        sess['teacher_dept'] = 'CSE'

    response = client.get('/teacher-dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Teacher Dashboard' in response.data