from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash

from app.models import db, User, Role, Status, Group
from run import app

cli = FlaskGroup(app)


@cli.command("createsu")
def create_superuser():
    role = Role.query.filter_by(name='Admin').first()
    if not role:
        print("run seeder first")
        return

    username = input("Enter superuser username: ")
    email = input("Enter superuser email: ")
    password = input("Enter superuser password: ")

    superuser = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        roles=Role.query.all(),
        groups=Group.query.all()
    )

    db.session.add(superuser)
    db.session.commit()
    print(f'Superuser {username} created successfully!')
    print(f'roles: {superuser.roles} \n groups: {superuser.groups}')


@cli.command("recreate_db")
def recreate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()


@cli.command("drop_db")
def drop_db():
    with app.app_context():
        db.drop_all()
        db.session.commit()


@cli.command("seed")
def seed_statuses_roles():
    st_1 = Status(name="Pending")
    st_2 = Status(name="In review")
    st_3 = Status(name="Closed")

    ro_1 = Role(name='Admin')
    ro_2 = Role(name='Manager')
    ro_3 = Role(name='Analyst')

    gr_1 = Group(name='Customer1')
    gr_2 = Group(name='Customer2')
    gr_3 = Group(name='Customer3')

    with app.app_context():
        db.session.add(st_1)
        db.session.add(st_2)
        db.session.add(st_3)
        db.session.add(ro_1)
        db.session.add(ro_2)
        db.session.add(ro_3)
        db.session.add(gr_1)
        db.session.add(gr_2)
        db.session.add(gr_3)
        db.session.commit()


if __name__ == "__main__":
    cli()
