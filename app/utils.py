import re
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request

from .config import Config
from .models import User, Ticket, Status, Group


def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')


def verify_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401

        user_id = verify_token(token)
        if not user_id:
            return {'message': 'Invalid token'}, 401

        user = get_user_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        kwargs['user'] = user
        return f(*args, **kwargs)

    return wrap


def role_required(role):
    def wrapper(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            user = kwargs['user']
            if not user:
                return {'message': 'Internal server error: User not found'}, 500
            if role not in str(user.roles):
                return {'message': 'Forbidden.'}, 403
            return f(*args, **kwargs)

        return wrap

    return wrapper


def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    print(re.match(pattern, email))
    return re.match(pattern, email)


def get_ticket_by_id(ticket_id):
    return Ticket.query.filter_by(id=ticket_id).first()


def validate_ticket(data, user):
    errors = {}
    try:
        note = data["note"]
        status_name = data["status"]
        group_name = data["group"]
        user_id = data["user_id"]
    except KeyError:
        errors["key_error"] = "Missing required parameters"
        return errors, None, None, None, None
    else:
        # Note validation
        if note is None:
            errors["note"] = "No note"

        # Status validation
        if status_name is None:
            errors["status"] = "No status provided"
        status = Status.query.filter_by(name=status_name).first()
        if status is None:
            errors["status"] = "Wrong status provided"

        # Group validation
        group = Group.query.filter_by(name=group_name).first()
        if group is None:
            errors["group"] = "Wrong group provided"

        # User validation
        assign_to_user = User.query.filter_by(id=user_id).first()
        if user_id and assign_to_user is None:
            errors["user_id"] = "User not found"

        return errors, note, status, group, assign_to_user
