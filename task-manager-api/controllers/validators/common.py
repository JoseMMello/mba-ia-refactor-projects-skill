from middlewares.error_handler import AppError

INVALID_BODY_MESSAGE = 'Dados inválidos'


def require_json_object(data, allow_empty=False):
    """The body must be a JSON object. An empty one is refused unless allow_empty is set."""
    if not isinstance(data, dict):
        raise AppError(INVALID_BODY_MESSAGE)
    if not data and not allow_empty:
        raise AppError(INVALID_BODY_MESSAGE)
    return data


def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)
