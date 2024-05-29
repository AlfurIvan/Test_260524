from app.models import User
from . import app, client, init_database, db  # noqa
from . import get_header


def test_user_list_authorized(client, init_database):
    # Authenticate the Manager user
    header = get_header("testuser2", "54321", client)
    response = client.get('/users', headers=header)

    assert response.status_code == 200
    assert len(response.json) > 1


def test_user_list_unauthorized(client, init_database):
    # Authenticate the Analyst user
    header = get_header('testuser3', '51423', client)
    response = client.get('/users', headers=header)
    assert response.status_code == 403
    assert response.json["message"] == "Forbidden."


def test_user_detail(client, init_database):
    header = get_header("testuser2", "54321", client)
    users = User.query.all()

    response = client.get(f'/users/{users[2].id}', headers=header)

    assert response.status_code == 200
    assert "id" in response.json
    assert "username" in response.json
    assert "email" in response.json
    assert "groups" in response.json
    assert "roles" in response.json


def test_user_detail_not_found(client, init_database):
    header = get_header("testuser2", "54321", client)
    response = client.get(f'/users/1024', headers=header)

    assert response.status_code == 404
    assert response.json["message"] == "User not found"


def test_user_put_patch(client, init_database):
    header = get_header("testadmin1", "12345", client)
    response = client.patch(f'/users/3', headers=header,
                            json={"username": "testanalyst", "groups": ['Customer1', "Customer2"]})
    assert response.status_code == 200
    assert response.json["message"] == "Successfully updated"
    assert response.json["user"]["username"] == "testanalyst"


def test_user_delete(client, init_database):
    header = get_header("testadmin1", "12345", client)
    victim = User(username="victim", email="some@mail.com")
    victim.set_password("123123")
    db.session.add(victim)
    db.session.commit()
    db.session.refresh(victim)
    response = client.delete(f'/users/{victim.id}', headers=header)

    assert response.status_code == 204
