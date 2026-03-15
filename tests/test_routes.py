def test_student_dashboard_requires_login(client):
    res = client.get("/student-dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/student" in res.location


def test_teacher_dashboard_requires_login(client):
    res = client.get("/teacher-dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/teacher" in res.location


def test_teacher_achievement_requires_login(client):
    res = client.get("/submit_achievements", follow_redirects=False)
    assert res.status_code == 302
