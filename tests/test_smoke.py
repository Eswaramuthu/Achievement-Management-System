def test_home_page_loads(client):
    res = client.get("/")
    assert res.status_code == 200
