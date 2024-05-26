from functools import wraps

from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app import db
from app.models import Ticket, Group, Status
from . import tickets_bp


def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_anonymous or role not in [r.name for r in current_user.roles]:
                return redirect(url_for('auth.unauthorized'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@tickets_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@tickets_bp.route('/tickets')
@login_required
def tickets():
    if 'Admin' in [r.name for r in current_user.roles]:
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter(Ticket.group_id.in_([g.id for g in current_user.groups])).all()

    return render_template('tickets.html', tickets=tickets)


@tickets_bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket(ticket_id):
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
        ticket.note = request.form['note']
        db.session.commit()
        return redirect(url_for('tickets.tickets'))
    groups = Group.query.all()
    statuses = Status.query.all()
    return render_template('ticket.html', ticket=ticket, groups=groups,  statuses=statuses)


@tickets_bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
@role_required('Manager')
def create_ticket():
    if request.method == 'POST':
        note = request.form['note']
        group_id = request.form['group_id']
        status_id = request.form['status_id']
        ticket = Ticket(note=note, group_id=group_id, status_id=status_id)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('tickets.tickets'))
    groups = Group.query.all()
    statuses = Status.query.all()
    return render_template('create_ticket.html', groups=groups, statuses=statuses)
