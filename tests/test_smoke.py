# tests/test_home.py


# =====================================================
# 🏠 Home Page Tests
# =====================================================

def test_home_page_loads(client):
    """Home page should load successfully."""

    response = client.get("/")

    assert response.status_code == 200
