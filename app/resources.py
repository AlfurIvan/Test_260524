from flask import request, jsonify
from flask_restful import Resource

from . import db
from .models import User
from .schemas import UserSchema
from .utils import generate_token, verify_token

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
    def get(self):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401

        user_id = verify_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        return user_schema.dump(user), 200
