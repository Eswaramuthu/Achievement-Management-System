# tests/test_route_auth_guards.py


# =====================================================
# 🔒 Route Authentication Guard Tests
# =====================================================

def test_student_dashboard_requires_login(client):
    """Student dashboard should redirect to login if user is not authenticated."""

    response = client.get("/student-dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert "/student" in response.location


def test_teacher_dashboard_requires_login(client):
    """Teacher dashboard should redirect to login if user is not authenticated."""

    response = client.get("/teacher-dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert "/teacher" in response.location


def test_teacher_achievement_requires_login(client):
    """Achievement submission page should require teacher authentication."""

    response = client.get("/submit_achievements", follow_redirects=False)

    assert response.status_code == 302
