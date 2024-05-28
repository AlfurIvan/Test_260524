from flask import request, jsonify
from flask_restful import Resource

from app import db
from app.models import User
from app.schemas import UserSchema
from app.utils import generate_token, login_required, validate_email

user_schema = UserSchema()


class Register(Resource):

    def get(self):
        return jsonify({
            "username": "JohnDoe",
            "email": "johndoe@gmail.com",
            "password": "<PASSWORD>",
            "confirm_password": "<PASSWORD>",
        })

    def post(self):
        data = request.get_json()

        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400

        if not validate_email(data["email"]):
            return {'message': 'Input valid email'}, 400
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400

        if data['password'] != data['confirm_password']:
            return {'message': 'Passwords are not matching'}, 400

        data.pop('confirm_password')

        errors = user_schema.validate(data)
        if errors:
            return errors, 400
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            token = generate_token(user.id)
            return {'token': token}, 200

        return {'message': 'Invalid credentials'}, 401


class UserProfile(Resource):

    @login_required
    def get(self, **kwargs):
        return user_schema.dump(kwargs.pop("user")), 200
