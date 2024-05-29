from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from app import db
from app.models import Ticket, Role
from app.schemas import ticket_schema
from app.utils import login_required, role_required, get_ticket_by_id, validate_ticket


class TicketList(Resource):
    @login_required
    def get(self, *args, **kwargs):
        """
        Get user tickets
        ---
        tags:
            - tickets
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
            description: Tickets retrieved successfully
            schema:
              type: array
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
        """
        Get ticket by ID
        ---
        tags:
          - tickets
        security:
          - BearerAuth: []
        parameters:
          - name: ticket_id
            in: path
            required: true
            type: integer
            description: ID of the ticket
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
        responses:
          200:
            description: Ticket retrieved successfully
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: ID of the ticket
                title:
                  type: string
                  description: Title of the ticket
                description:
                  type: string
                  description: Description of the ticket
                user_id:
                  type: integer
                  description: ID of the user who created the ticket
                group_id:
                  type: integer
                  description: ID of the group associated with the ticket
                # Add other ticket fields here as needed
          404:
            description: Ticket not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Ticket not found
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
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Internal server error
        """
        ticket = get_ticket_by_id(ticket_id)
        if ticket is not None:
            user = kwargs["user"]
            if ticket.group not in user.groups and ticket.user != user:
                return {"message": "You are not allowed to see tickets from another groups"}, 403
            else:
                return ticket_schema.dump(ticket), 200
        else:
            return {"message": "Ticket not found"}, 404

    @login_required
    @role_required("Manager")
    def put(self, ticket_id, *args, **kwargs):
        """
        Update ticket by ID
        ---
        tags:
          - tickets
        security:
          - BearerAuth: []
        parameters:
          - name: ticket_id
            in: path
            required: true
            type: integer
            description: ID of the ticket
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
        responses:
          200:
            description: Ticket updated successfully
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: ID of the ticket
                title:
                  type: string
                  description: Title of the ticket
                description:
                  type: string
                  description: Description of the ticket
                user_id:
                  type: integer
                  description: ID of the user who created the ticket
                group_id:
                  type: integer
                  description: ID of the group associated with the ticket
                # Add other ticket fields here as needed
          400:
            description: Bad request (e.g., validation errors)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
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
        user = kwargs["user"]

        data = request.get_json()

        errors, note, status, group, assign_to_user = validate_ticket(data, user)
        if errors:
            return {"message": errors}, 400

        ticket = get_ticket_by_id(ticket_id)
        print(user.groups, ticket.group)
        if ticket.group not in user.groups and ticket.user != user:
            return {"message": "You are not allowed to see or modify tickets from another groups"}, 403

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
        """
        Delete ticket by ID
        ---
        tags:
          - tickets
        security:
          - BearerAuth: []
        parameters:
          - name: ticket_id
            in: path
            required: true
            type: integer
            description: ID of the ticket
          - name: Authorization
            in: header
            required: true
            type: string
            description: JWT token for authorization (e.g., Bearer <token>)
        responses:
          204:
            description: Ticket deleted successfully
          404:
            description: Ticket not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
                  example: Ticket not found
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
        """
        Get ticket creation parameters
        ---
        tags:
          - tickets
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
            description: Ticket creation parameters retrieved successfully
            schema:
              type: object
              properties:
                note:
                  type: string
                  description: Note for the ticket
                  example: Abra Cadabra Avada Kedavra
                status:
                  type: string
                  description: Status of the ticket
                  example: Pending/In review/Closed
                group:
                  type: string
                  description: Group associated with the ticket
                  example: CustomerX
                user_id:
                  type: integer
                  description: ID of the user creating the ticket
                  example: user.id
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
        return jsonify({
            "note": "Abra Cadabra Avada Kedavra",
            "status": "Pending/In review/Closed",
            "group": "CustomerX",
            "user_id": "user.id ",
        })

    @login_required
    @role_required("Manager")
    def post(self, *args, **kwargs):
        """
        Create a new ticket
        ---
        tags:
          - tickets
        security:
          - BearerAuth: []
        parameters:
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
                note:
                  type: string
                  description: Note for the ticket
                status:
                  type: string
                  description: Status of the ticket
                group:
                  type: string
                  description: Group associated with the ticket
                user_id:
                  type: integer
                  description: ID of the user to whom the ticket is assigned
        responses:
          201:
            description: Ticket created successfully
            schema:
              $ref: '#/definitions/Ticket'
          400:
            description: Bad request (e.g., validation errors)
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
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
        user = kwargs["user"]
        data = request.get_json()

        errors, note, status, group, assign_to_user = validate_ticket(data, user)
        if errors:
            return {"message": errors}, 400
        print(user.groups, group)
        if group not in user.groups and "Admin" not in str(user.roles):
            return {"message": "You are not allowed to create tickets for other groups"}, 403
        ticket = Ticket(
            note=note,
            status=status,
            group=group,
            user=assign_to_user
        )
        db.session.add(ticket)
        db.session.commit()

        return ticket_schema.dump(ticket), 201
