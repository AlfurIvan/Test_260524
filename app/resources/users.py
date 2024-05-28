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
        users = User.query.all()
        return user_schema.dump(users, many=True), 200


class UserDetail(Resource):
    @login_required
    @role_required('Manager')
    def get(self, user_id, *args, **kwargs):
        user = get_user_by_id(user_id)
        if user is None:
            return user_schema.dump(user), 200
        return {"message": "User not found"}, 404

    @login_required
    @role_required('Admin')
    def put(self, user_id, *args, **kwargs):
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
        return self.put(user_id)

    @login_required
    @role_required('Admin')
    def delete(self, user_id, *args, **kwargs):
        user = get_user_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        else:
            db.session.delete(user)
            db.session.commit()
            return {}, 204
