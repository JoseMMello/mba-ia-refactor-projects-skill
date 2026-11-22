from middlewares.error_handler import AppError
from models.user import DEFAULT_ROLE, MIN_PASSWORD_LENGTH, USER_ROLES
from utils.helpers import validate_email

INVALID_EMAIL_MESSAGE = 'Email inválido'
INVALID_ROLE_MESSAGE = 'Role inválido'


def _require_text(value, required_message, invalid_message):
    if not value:
        raise AppError(required_message)
    if not isinstance(value, str):
        raise AppError(invalid_message)
    return value


def validate_name(name):
    return _require_text(name, 'Nome é obrigatório', 'Nome inválido')


def validate_email_format(email):
    if not validate_email(email):
        raise AppError(INVALID_EMAIL_MESSAGE)
    return email


def validate_password(password, too_short_message):
    if not isinstance(password, str):
        raise AppError('Senha inválida')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(too_short_message)
    return password


def validate_role(role):
    if not isinstance(role, str) or role not in USER_ROLES:
        raise AppError(INVALID_ROLE_MESSAGE)
    return role


def validate_active(active):
    if not isinstance(active, bool):
        raise AppError('Campo active inválido')
    return active


def validate_new_user(data):
    """Presence and format of the fields of a new user. Role is checked after the e-mail lookup."""
    name = validate_name(data.get('name'))
    email = _require_text(data.get('email'), 'Email é obrigatório', INVALID_EMAIL_MESSAGE)
    password = _require_text(data.get('password'), 'Senha é obrigatória', 'Senha inválida')
    validate_email_format(email)
    validate_password(password, f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
    return {
        'name': name,
        'email': email,
        'password': password,
        'role': data.get('role', DEFAULT_ROLE),
    }


def validate_credentials(data):
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise AppError('Email e senha são obrigatórios')
    if not isinstance(email, str) or not isinstance(password, str):
        raise AppError('Email e senha são obrigatórios')
    return email, password
