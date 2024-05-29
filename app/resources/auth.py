from flask import request, jsonify
from flask_restful import Resource

from app import db
from app.models import User
from app.schemas import user_schema
from app.utils import generate_token, login_required, validate_email


class Register(Resource):

    def get(self):
        """
        Show structure hint
        ---
        tags:
          - auth
        responses:
          200:
            description: User details retrieved successfully
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: Username of the user
                  example: "JohnDoe"
                email:
                  type: string
                  description: Email of the user
                  example: "johndoe@gmail.com"
                password:
                  type: string
                  description: Password of the user
                  example: "<PASSWORD>"
                confirm_password:
                  type: string
                  description: Confirmation of the password
                  example: "<PASSWORD>"
          500:
            description: Internal server error
        """
        return jsonify({
            "username": "JohnDoe",
            "email": "johndoe@gmail.com",
            "password": "<PASSWORD>",
            "confirm_password": "<PASSWORD>",
        })

    def post(self):
        """
        Register a new user
        ---
        tags:
          - auth
        parameters:
          - in: body
            name: body
            schema:
              type: object
              required:
                - username
                - email
                - password
                - confirm_password
              properties:
                username:
                  type: string
                  description: Username of the new user
                email:
                  type: string
                  description: Email of the new user
                password:
                  type: string
                  description: Password for the new user
                confirm_password:
                  type: string
                  description: Confirmation of the password
        responses:
          201:
            description: User registered successfully
          400:
            description: Bad request (e.g., validation errors)
        """
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
        """
        Login a user
        ---
          tags:
            - auth
          parameters:
            - in: body
              name: body
              schema:
                type: object
                required:
                  - username
                  - password
                properties:
                  username:
                    type: string
                    description: Username of the user
                  password:
                    type: string
                    description: Password of the user
          responses:
            200:
              description: Successful login
              schema:
                type: object
                properties:
                  token:
                    type: string
                    description: Authentication token
            401:
              description: Invalid credentials
              schema:
                type: object
                properties:
                  message:
                    type: string
                    description: Error message
                    example: Invalid credentials
            500:
              description: Internal server error
        """
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            token = generate_token(user.id)
            return {'token': token}, 200

        return {'message': 'Invalid credentials'}, 401


class UserProfile(Resource):

    @login_required
    def get(self, **kwargs):
        """
        Show user profile details
        ---
        tags:
          - auth
        security:
          - BearerAuth: []
        parameters:
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
        responses:
          200:
            description: User information retrieved successfully
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: Username of the user
                email:
                  type: string
                  description: Email of the user
                # Add other user fields here as needed
          401:
            description: Unauthorized (invalid or missing token)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Unauthorized
          500:
            description: Internal server error
        """
        return user_schema.dump(kwargs.pop("user")), 200
