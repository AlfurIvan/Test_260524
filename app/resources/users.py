from flask import request
from flask_restful import Resource

from app import db
from app.models import User, Role, Group
from app.schemas import user_schema
from app.utils import get_user_by_id, login_required, role_required, validate_email


class UserList(Resource):

    @login_required
    @role_required('Manager')
    def get(self, *args, **kwargs):
        """
        Get list of users
        ---
        tags:
        - users
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
            description: List of users retrieved successfully
            schema:
              type: array
              items:
                schena
          401:
            description: Unauthorized (invalid or missing token)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Unauthorized
          403:
            description: Forbidden (user does not have required role)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Insufficient permissions
          500:
            description: Internal server error
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Internal server error
        """
        users = User.query.all()
        return user_schema.dump(users, many=True), 200


class UserDetail(Resource):
    @login_required
    @role_required('Manager')
    def get(self, user_id, *args, **kwargs):
        """
        Get user by ID
        ---
        tags:
          - users
        security:
          - BearerAuth: []
        parameters:
          - name: user_id
            in: path
            required: true
            type: integer
            description: ID of the user
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
        responses:
          200:
            description: User retrieved successfully
            schema:
              $ref: '#/definitions/User'
          404:
            description: User not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: User not found
          401:
            description: Unauthorized (invalid or missing token)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Unauthorized
          403:
            description: Forbidden (user does not have required role)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Insufficient permissions
          500:
            description: Internal server error
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Internal server error
        """
        user = get_user_by_id(user_id)
        if user is not None:
            return user_schema.dump(user), 200
        return {"message": "User not found"}, 404

    @login_required
    @role_required('Admin')
    def put(self, user_id, *args, **kwargs):
        """
        Update user by ID
        ---
        tags:
          - users
        security:
          - BearerAuth: []
        parameters:
          - name: user_id
            in: path
            required: true
            type: integer
            description: ID of the user
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: New username for the user
                email:
                  type: string
                  format: email
                  description: New email for the user
                roles:
                  type: array
                  description: New roles for the user
                  items:
                    type: string
                  example: ["Manager", "Employee"]
                groups:
                  type: array
                  description: New groups for the user
                  items:
                    type: string
                  example: ["GroupA", "GroupB"]
        responses:
          200:
            description: User updated successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Success message
                  example: Successfully updated
                user:
                  $ref: '#/definitions/User'
          400:
            description: Bad request (e.g., validation errors)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
          404:
            description: User not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: User not found
          401:
            description: Unauthorized (invalid or missing token)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Unauthorized
          403:
            description: Forbidden (user does not have required role)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Insufficient permissions
          500:
            description: Internal server error
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Internal server error
          """
        data = request.get_json()
        user = get_user_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404

        errors = {}
        if "username" in data:
            if User.query.filter_by(username=data["username"]).first():
                errors["username"] = "Username already exists."
            else:
                user.username = data["username"]
        if "email" in data:
            if validate_email(data["email"]) is None:
                errors["email"] = "Invalid email."
            elif User.query.filter_by(email=data["email"]).first():
                errors["email"] = "Email already exists."
            else:
                user.email = data["email"]
        if errors:
            return {"message": errors}, 400

        if "roles" in data:
            user.roles = [Role.query.filter_by(name=role).first() for role in data["roles"]]
            # To remove consequences possibility after inputting any not existing roles
            while None in user.roles:
                user.roles.remove(None)

        if "groups" in data:
            user.groups = [Group.query.filter_by(name=group).first() for group in data["groups"]]
            # To remove consequences possibility after inputting any not existing groups
            while None in user.groups:
                user.groups.remove(None)
        db.session.commit()
        return {"message": "Successfully updated", "user": user_schema.dump(user)}, 200

    @login_required
    @role_required('Admin')
    def patch(self, user_id, *args, **kwargs):
        """
        Patch user by ID
        ---
        tags:
          - users
        security:
          - BearerAuth: []
        parameters:
          - name: user_id
            in: path
            required: true
            type: integer
            description: ID of the user
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  description: New username for the user
                email:
                  type: string
                  format: email
                  description: New email for the user
                roles:
                  type: array
                  description: New roles for the user
                  items:
                    type: string
                  example: ["Manager", "Employee"]
                groups:
                  type: array
                  description: New groups for the user
                  items:
                    type: string
                  example: ["GroupA", "GroupB"]
        responses:
          200:
            description: User updated successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Success message
                  example: Successfully updated
                user:
                  $ref: '#/definitions/User'
          400:
            description: Bad request (e.g., validation errors)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
          404:
            description: User not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: User not found
          401:
            description: Unauthorized (invalid or missing token)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Unauthorized
          403:
            description: Forbidden (user does not have required role)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Insufficient permissions
          500:
            description: Internal server error
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Internal server error
        """
        return self.put(user_id)

    @login_required
    @role_required('Admin')
    def delete(self, user_id, *args, **kwargs):
        """
        Delete user by ID
        ---
        tags:
          - users
        security:
          - BearerAuth: []
        parameters:
          - name: user_id
            in: path
            required: true
            type: integer
            description: ID of the user
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
        responses:
          204:
            description: User deleted successfully
          404:
            description: User not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: User not found
          401:
            description: Unauthorized (invalid or missing token)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Unauthorized
          403:
            description: Forbidden (user does not have required role)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Insufficient permissions
          500:
            description: Internal server error
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Internal server error
        """
        user = get_user_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        else:
            db.session.delete(user)
            db.session.commit()
            return {}, 204
