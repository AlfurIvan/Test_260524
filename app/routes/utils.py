from functools import wraps
from flask_login import current_user
from flask import redirect, url_for


def role_required(role):
    """Checks if the current user have some role or not."""
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_anonymous or role not in [r.name for r in current_user.roles]:
                return redirect(url_for('auth.forbidden'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
