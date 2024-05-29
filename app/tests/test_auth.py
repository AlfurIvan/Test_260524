from app.models import User
from . import app, client, init_database  # noqa
from . import get_header


def test_register(client, init_database):
    # Test valid registration
    data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    response = client.post('/register', json=data)
    assert response.status_code == 201

    # Test registration with existing username
    response = client.post('/register', json=data)
    assert response.status_code == 400
    assert response.json['message'] == 'Username already exists'


def test_login(client, init_database):
    # Test valid login
    print(User.query.all())
    data = {"username": "testuser2", "password": "54321"}
    response = client.post('/login', json=data)
    assert response.status_code == 200
    assert 'token' in response.json

    # Test invalid login
    data = {"username": "testuser2", "password": "wrong_password"}
    response = client.post('/login', json=data)
    assert response.status_code == 401


def test_profile(client, init_database):
    header = get_header("testuser2", "54321", client)
    response = client.get('/profile', headers=header)
    assert response.status_code == 200
    assert response.json['username'] == 'testuser2'
    assert "email" in response.json
    assert "groups" in response.json
    assert "roles" in response.json
