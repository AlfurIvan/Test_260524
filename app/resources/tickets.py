from flask import request
from flask_restful import Resource
from sqlalchemy.sql.functions import current_user

from app import db
from app.models import User
from app.schemas import UserSchema
from app.utils import get_user_by_id, login_required, role_required, validate_email


class TicketList(Resource):
    @login_required
    def get(self):
        if current_user.role != "Admin":
            return {"message": "Only Admin can get tickets"}, 403
        else:
            return {"message": "Welcome, master"}, 200