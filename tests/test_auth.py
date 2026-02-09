def test_student_login_success(client):
    res = client.post(
        "/student",
        data={
            "sname": "S001",
            "password": "password"
        },
        follow_redirects=True
    )

    assert res.status_code == 200
    assert b"Student Dashboard" in res.data



def test_student_login_failure(client):
    res = client.post("/student", data={
        "sname": "S001",
        "password": "wrong"
    })

    assert res.status_code == 200
    assert b"Invalid credentials" in res.data


def test_teacher_login_success(client):
    res = client.post(
        "/teacher",
        data={
            "tname": "T001",
            "password": "password"
        },
        follow_redirects=True
    )

    assert res.status_code == 200
    assert b"Teacher Dashboard" in res.data



def test_teacher_login_failure(client):
    res = client.post("/teacher", data={
        "tname": "T001",
        "password": "wrong"
    })

    assert res.status_code == 200
    assert b"Teacher Login" in res.data
