# tests/test_protected_routes.py


# =====================================================
# 🔒 Protection Tests (Unauthenticated Access)
# =====================================================

def test_student_dashboard_protected(client):
    """Student dashboard should redirect to login if not authenticated."""

    response = client.get("/student-dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert "/student" in response.location


def test_teacher_dashboard_protected(client):
    """Teacher dashboard should redirect to login if not authenticated."""

    response = client.get("/teacher-dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert "/teacher" in response.location


# =====================================================
# ✅ Authenticated Access Tests
# =====================================================

def test_authenticated_student_access(client):
    """Authenticated student should access dashboard successfully."""

    with client.session_transaction() as sess:
        sess.update({
            "logged_in": True,
            "student_id": "S12345",
            "student_name": "Test Student",
            "student_dept": "CSE",
        })

    response = client.get("/student-dashboard", follow_redirects=True)

    assert response.status_code == 200
    assert b"Student Dashboard" in response.data


def test_authenticated_teacher_access(client):
    """Authenticated teacher should access dashboard successfully."""

    with client.session_transaction() as sess:
        sess.update({
            "logged_in": True,
            "teacher_id": "T001",
            "teacher_name": "Test Teacher",
            "teacher_dept": "CSE",
        })

    response = client.get("/teacher-dashboard", follow_redirects=True)

    assert response.status_code == 200
    assert b"Teacher Dashboard" in response.data
