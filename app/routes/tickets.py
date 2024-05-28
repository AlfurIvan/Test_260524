from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import Ticket, Group, Status, User
from . import tickets_bp
from .utils import role_required


@tickets_bp.route('/')
@login_required
def index():
    """Welcome page."""
    return render_template('tickets/index.html')


@tickets_bp.route('/tickets')
@login_required
def tickets():
    """List of all tickets."""
    if 'Admin' in [r.name for r in current_user.roles]:
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter(
            or_(
                Ticket.group_id.in_([g.id for g in current_user.groups]),
                Ticket.user_id == current_user.id
            )
        ).all()

    return render_template('tickets/tickets.html', tickets=tickets)


@tickets_bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket(ticket_id):
    """detailed ticket wiev"""
    ticket = Ticket.query.get(ticket_id)
    roles = current_user.roles
    groups = current_user.groups
    if not ticket:
        return redirect(url_for('tickets.tickets'))
    if ticket.group_id not in [g.id for g in groups]:
        return redirect(url_for('auth.forbidden'))
    if request.method == 'POST':
        if 'Manager' not in [r.name for r in roles]:
            return redirect(url_for('auth.forbidden'))
        ticket.status = Status.query.filter_by(id=request.form['status_id']).first()
        ticket.group = Group.query.filter_by(id=request.form['group_id']).first()
        ticket.user = User.query.filter_by(id=request.form['user_id']).first()
        ticket.note = request.form['note']
        db.session.commit()
        return redirect(url_for('tickets.tickets'))
    groups = Group.query.all()
    statuses = Status.query.all()
    users = User.query.all()
    return render_template('tickets/ticket.html', ticket=ticket, groups=groups, statuses=statuses, users=users)


@tickets_bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
@role_required('Manager')
def create_ticket():
    """Create a new ticket(if you are a manager)."""
    if request.method == 'POST':
        note = request.form['note']
        group_id = request.form['group_id']
        status_id = request.form['status_id']
        user_id = request.form['user_id']
        ticket = Ticket(note=note, group_id=group_id, status_id=status_id, user_id=user_id)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('tickets.tickets'))
    groups = Group.query.all()
    statuses = Status.query.all()
    users = User.query.all()
    return render_template(
        'tickets/create_ticket.html',
        groups=groups,
        statuses=statuses,
        users=users
    )
