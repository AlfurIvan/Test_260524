from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User
from . import auth_bp


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rep_password = request.form['rep_password']

        err = ''
        if password != rep_password:
            err = "Passwords do not match"
        if not password:
            err = "Input password and repeat password"
        if not username:
            err = "Input username"

        if not err:
            try:
                user = User(username=username, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                err = "User already exists"

        if not err:
            return redirect(url_for('auth.login'))
    return render_template("register.html")


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
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/unauthorized')
def unauthorized():
    return render_template("403.html")
