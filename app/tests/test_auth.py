from ..models import User, Role, Group


def test_register(client, init_database):
    response = client.post('/register', data=dict(
        username='newuser',
        email='newuser@example.com',
        password='newpassword',
        rep_password='newpassword'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert User.query.filter_by(username='newuser').first() is not None


def test_login(client, init_database):
    response = client.post('/login', data=dict(
        username='testuser3',
        password='51423'
    ), follow_redirects=True)
    assert response.status_code == 200


def test_users_without_login(client, init_database):
    response1 = client.get('/users')
    assert response1.status_code == 302
    response2 = client.get('/users/1')
    assert response2.status_code == 302


def test_inappropriate_role(client, init_database):
    login = client.post(
        '/login',
        data=dict(username='testuser3', password='51423'),
        follow_redirects=True
    )
    assert login.status_code == 200
    response1 = client.get('/users')
    assert response1.status_code == 302
    assert b'forbidden' in response1.data
    response2 = client.get('/users/1')
    assert response2.status_code == 302
    assert b'forbidden' in response1.data


def test_view_user_details(client, init_database):
    login = client.post('/login', data=dict(username='testadmin1', password='12345'), follow_redirects=True)
    assert login.status_code == 200
    user = User.query.filter_by(username='testuser2').first()
    response = client.get(f'/users/{user.id}')

    assert response.status_code == 200
    print(response.data)
    assert b'testuser2' in response.data
    assert b'test2@example.com' in response.data


def test_edit_user_roles_groups(client, init_database):
    client.post('/login', data=dict(
        username='testadmin1',
        password='12345'
    ), follow_redirects=True)

    user = User.query.filter_by(username='testuser2').first()
    role = Role.query.filter_by(name='Admin').first()
    group = Group.query.filter_by(name='Customer1').first()
    response = client.post(f'/users/{user.id}', data=dict(
        roles=[str(role.id)],
        groups=[str(group.id)]
    ), follow_redirects=True)
    user = User.query.filter_by(username='testuser2').first()
    assert response.status_code == 200
    assert role in user.roles
    assert group in user.groups
