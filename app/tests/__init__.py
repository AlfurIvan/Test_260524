import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Role, Group, Status, Ticket


class Config(object):
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ticketsystem_test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


test_config = Config()


@pytest.fixture
def app():
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def init_database():
    # Insert roles and users for testing
    st_1 = Status(name="Pending")
    st_2 = Status(name="In review")
    st_3 = Status(name="Closed")

    ro_1 = Role(name='Admin')
    ro_2 = Role(name='Manager')
    ro_3 = Role(name='Analyst')

    gr_1 = Group(name='Customer1')
    gr_2 = Group(name='Customer2')
    gr_3 = Group(name='Customer3')

    user1 = User(
        username='testadmin1',
        email='test1@example.com',
        password=generate_password_hash('12345'),
        roles=[ro_1, ro_2, ro_3],
        groups=[gr_1, gr_2, gr_3]
    )
    user2 = User(
        username='testuser2',
        email='test2@example.com',
        password=generate_password_hash('54321'),
        roles=[ro_2],
        groups=[gr_2]
    )

    user3 = User(
        username='testuser3',
        email='test3@example.com',
        password=generate_password_hash('51423'),
        roles=[ro_3],
        groups=[gr_2]
    )

    t1 = Ticket(
        note="Ticket 1",
        status=st_1,
        group=gr_1,
    )
    t2 = Ticket(
        note="Ticket 2",
        status=st_2,
        group=gr_2
    )
    t3 = Ticket(
        note="Ticket 3",
        status=st_3,
        group=gr_3,
        user=user3
    )


    db.session.add(st_1)
    db.session.add(st_2)
    db.session.add(st_3)
    db.session.add(ro_1)
    db.session.add(ro_2)
    db.session.add(ro_3)
    db.session.add(gr_1)
    db.session.add(gr_2)
    db.session.add(gr_3)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(t1)
    db.session.add(t2)
    db.session.add(t3)
    db.session.commit()
    yield db
    db.session.remove()
    db.drop_all()

def get_header(un, pwd, client):
    """DRY"""
    login_resp = client.post('/login', json={'username': un, 'password': pwd})
    try:
        token = login_resp.json['token']
    except KeyError:
        raise KeyError("Wrong credentials are passed to get_header() in tests")
    else:
        return {'Authorization': token}
