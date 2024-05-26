from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
tickets_bp = Blueprint('tickets', __name__)

from . import auth
from . import tickets