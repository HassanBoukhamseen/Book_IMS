import pytest
from fastapi.testclient import TestClient
from api import app  

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client

# @pytest.fixture(scope="module")
def test_register_user(test_client):
    response = test_client.post("/users/register", json={
        "username": "email_15@gmail.com",
        "password": "password_15"
    })
    assert response.status_code == 200
    assert "message" in response.json()

# @pytest.fixture(scope="module")
def test_login_user(test_client):
    response = test_client.post("/users/login", json={
        "username": "email_15@gmail.com",
        "password": "password_15"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_get_current_user(test_client):
    
    login_response = test_client.post("/users/login", json={
        "username": "email_15@gmail.com",
        "password": "password_15"
    })
    access_token = login_response.json()["access_token"]

    # Use the token to get the current user
    response = test_client.get("/users/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "testuser"

def test_update_current_user(test_client):
    login_response = test_client.post("/users/login", json={
        "username": "email_15@gmail.com",
        "password": "password_15"
    })
    access_token = login_response.json()["access_token"]

    # Update user info
    response = test_client.put("/users/me", headers={
        "Authorization": f"Bearer {access_token}"
    }, json={
        "username": "updateduser"
    })
    assert response.status_code == 200
    assert "message" in response.json()
    assert "token" in response.json()

def test_get_book_recommendations(test_client):
    # First, login to get the token
    login_response = test_client.post("/users/login", json={
        "username": "email_15@gmail.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]

    # Get book recommendations
    response = test_client.get("/recommendations", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    assert "book_recommendations" in response.json()

def test_health_check(test_client):
    response = test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() is True