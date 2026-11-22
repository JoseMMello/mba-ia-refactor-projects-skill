import hmac
from functools import wraps

from flask import request

from config.settings import settings
from middlewares.error_handler import AppError

ADMIN_TOKEN_HEADER = "X-Admin-Token"
HTTP_FORBIDDEN = 403


def require_admin(view):
    """Allow the request only with the configured admin token.

    With no ADMIN_TOKEN configured, the route is disabled.
    """
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = settings.ADMIN_TOKEN
        received = request.headers.get(ADMIN_TOKEN_HEADER, "")
        if not expected or not hmac.compare_digest(received.encode("utf-8"), expected.encode("utf-8")):
            raise AppError("Acesso negado", HTTP_FORBIDDEN)
        return view(*args, **kwargs)

    return wrapper
