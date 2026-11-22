import hmac
from functools import wraps

from flask import request

from config.settings import settings
from middlewares.error_handler import AppError

ADMIN_TOKEN_HEADER = 'X-Admin-Token'
FORBIDDEN_MESSAGE = 'Acesso negado'


def is_admin_request():
    """True when the request carries the admin token configured in ADMIN_TOKEN."""
    expected = settings.ADMIN_TOKEN
    if not expected:
        return False
    received = request.headers.get(ADMIN_TOKEN_HEADER, '')
    return hmac.compare_digest(received.encode('utf-8'), expected.encode('utf-8'))


def ensure_admin():
    if not is_admin_request():
        raise AppError(FORBIDDEN_MESSAGE, 403)


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        ensure_admin()
        return view(*args, **kwargs)
    return wrapper
