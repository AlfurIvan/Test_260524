from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from app import db
from app.models import Ticket
from app.schemas import ticket_schema
from app.utils import login_required, role_required, get_ticket_by_id, validate_ticket


class TicketList(Resource):
    @login_required
    def get(self, *args, **kwargs):
        user = kwargs["user"]
        if "Admin" in str(user.roles):
            tickets = Ticket.query.all()
        else:
            tickets = Ticket.query.filter(
                or_(
                    Ticket.group_id.in_([g.id for g in user.groups]),
                    Ticket.user_id == user.id
                )
            ).all()
        return ticket_schema.dump(tickets, many=True), 200


class TicketDetail(Resource):
    @login_required
    def get(self, ticket_id, *args, **kwargs):
        ticket = get_ticket_by_id(ticket_id)
        if ticket is not None:
            return ticket_schema.dump(ticket), 200
        else:
            return {"message": "Ticket not found"}, 404

    @login_required
    @role_required("Manager")
    def put(self, ticket_id, *args, **kwargs):
        user = kwargs["user"]
        data = request.get_json()

        errors, note, status, group, assign_to_user = validate_ticket(data, user)
        if errors:
            return {"message": errors}, 400

        ticket = get_ticket_by_id(ticket_id)
        ticket.note = note
        ticket.status = status
        ticket.group = group
        ticket.user = assign_to_user
        db.session.commit()
        return ticket_schema.dump(ticket), 200

    # @login_required  # влом
    # @role_required("Manager")
    # def patch(self, ticket_id, *args, **kwargs):
    #     data = request.get_json()

    @login_required
    @role_required("Manager")
    def delete(self, ticket_id, *args, **kwargs):
        ticket = get_ticket_by_id(ticket_id)
        if not ticket:
            return {"message": "Ticket not found"}, 404
        else:
            db.session.delete(ticket)
            db.session.commit()
            return {}, 204


class TicketCreate(Resource):
    @login_required
    @role_required("Manager")
    def get(self, *args, **kwargs):
        return jsonify({
            "note": "Abra Cadabra Avada Kedavra",
            "status": "Pending/In review/Closed",
            "group": "CustomerX",
            "user_id": "user.id ",
        })

    @login_required
    @role_required("Manager")
    def post(self, *args, **kwargs):
        user = kwargs["user"]
        data = request.get_json()

        errors, note, status, group, assign_to_user = validate_ticket(data, user)
        if errors:
            return {"message": errors}, 400

        ticket = Ticket(
            note=note,
            status=status,
            group=group,
            user=assign_to_user
        )
        db.session.add(ticket)
        db.session.commit()

        return ticket_schema.dump(ticket), 201
