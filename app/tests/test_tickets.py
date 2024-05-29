from app.models import Ticket, Status, Group
from . import app, client, init_database, db  # noqa
from . import get_header


def test_ticket_list_admin(client, init_database):
    # Authenticate the Admin user
    header = get_header("testadmin1", "12345", client)
    response = client.get('/tickets', headers=header)

    assert response.status_code == 200
    assert len(response.json) == 3


def test_ticket_list_analyst(client, init_database):
    # Authenticate the Analyst user
    header = get_header("testuser3", "51423", client)
    response = client.get('/tickets', headers=header)

    assert response.status_code == 200
    assert len(response.json) == 2


def test_ticket_detail_analyst(client, init_database):
    header = get_header("testuser3", "51423", client)
    # Ticket from other group
    response = client.get('/tickets/1', headers=header)
    assert response.status_code == 403
    assert response.json["message"] == "You are not allowed to see tickets from another groups"
    # Ticket from same group
    response = client.get('/tickets/2', headers=header)
    assert response.status_code == 200
    assert "note" in response.json
    # Ticket assigned to user
    response = client.get('/tickets/3', headers=header)
    assert response.status_code == 200
    assert "note" in response.json


def test_ticket_detail_put(client, init_database):
    # Auth Manager
    header = get_header("testuser2", "54321", client)
    # Manager cannot access other group
    response = client.put('/tickets/1', headers=header,
                          json={"note": "Modified Ticket 1",
                                "status": 'Closed',
                                "group": "Customer2",
                                "user_id": ''})
    assert response.status_code == 403
    # But can access same group
    response = client.put('/tickets/3', headers=header,
                          json={"note": "Modified Ticket 2",
                                "status": 'Closed',
                                "group": "Customer2",
                                "user_id": ''})
    assert response.status_code == 200
    assert response.json["note"] == "Modified Ticket 2"
    assert response.json["status"]["name"] == "Closed"


def test_ticket_delete(client, init_database):
    status = Status.query.filter_by(name='Closed').first()
    group = Group.query.filter_by(name="Customer2").first()
    victim = Ticket(
        note="Born to Die",
        status=status,
        group=group
    )
    db.session.add(victim)
    db.session.commit()
    db.session.refresh(victim)
    header = get_header("testuser2", "54321", client)
    response = client.delete(f'/tickets/{victim.id}', headers=header)
    assert response.status_code == 204


def test_ticket_create_get(client, init_database):
    header = get_header("testuser2", "54321", client)
    response = client.get('/create-ticket', headers=header)
    assert response.status_code == 200
    assert "note" in response.json
    assert "status" in response.json
    assert "group" in response.json
    assert "user_id" in response.json


def test_ticket_create_post(client, init_database):
    header = get_header("testuser2", "54321", client)
    # Same group
    response = client.post('/create-ticket', headers=header,
                           json={
                               "note": "Abra Cadabra Avada Kedavra",
                               "status": "Pending",
                               "group": "Customer2",
                               "user_id": "",
                           })
    assert response.status_code == 201
    assert "note" in response.json
    # Other group
    response = client.post('/create-ticket', headers=header,
                           json={
                               "note": "Abra Cadabra Avada Kedavra",
                               "status": "Pending",
                               "group": "Customer1",
                               "user_id": "",
                           })
    assert response.status_code == 403
    assert "message" in response.json
    # Uncompleted document passed
    response = client.post('/create-ticket', headers=header,
                           json={
                               "note": "Abra Cadabra Avada Kedavra",
                               "status": "Pending",
                               "user_id": "",
                           })
    assert response.status_code == 400
    assert "message" in response.json
