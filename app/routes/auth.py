from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User, Role, Group
from . import auth_bp
from .tickets import role_required

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        rep_password = request.form['rep_password']

        err = ''
        if password != rep_password:
            err = "Passwords do not match"
        if not password:
            err = "Input password and repeat password"
        if not email:
            err = "Input email"
        if not username:
            err = "Input username"

        if not err:
            try:
                user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    roles=[Role.query.filter_by(name="Analyst").first()]
                )
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                err = "User already exists"

        if not err:
            return redirect(url_for('auth.login'))
        else:
            flash(err)
    return render_template("auth/register.html")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('tickets.index'))
        else:
            flash('Invalid credentials')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/unauthorized')
def unauthorized():
    return render_template("exc/401.html")


@auth_bp.route('/forbidden')
def forbidden():
    return render_template("exc/403.html")


@auth_bp.route('/users', methods=['GET'])
@login_required
@role_required('Manager')
def users():
    users = User.query.all()
    return render_template("users/users.html", users=users)

@auth_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def user(user_id):
    user = User.query.get_or_404(user_id)
    all_roles = Role.query.all()
    all_groups = Group.query.all()
    return render_template('users/user.html', user=user, all_roles=all_roles, all_groups=all_groups)


@auth_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
def edit_user(user_id):
    if 'Admin' not in [role.name for role in current_user.roles]:
        return redirect(url_for('.forbidden', user_id=user_id))

    user = User.query.get_or_404(user_id)

    roles = request.form.getlist('roles')
    groups = request.form.getlist('groups')

    user.roles = [Role.query.get(role_id) for role_id in roles]
    user.groups = [Group.query.get(group_id) for group_id in groups]

    db.session.commit()
    flash('User updated successfully.')
    return redirect(url_for('auth.user', user_id=user.id))