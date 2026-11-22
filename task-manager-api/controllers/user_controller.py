import logging

from flask import jsonify, request

from controllers.validators.common import require_json_object
from controllers.validators.user_validator import (
    validate_active, validate_credentials, validate_email_format, validate_name,
    validate_new_user, validate_password, validate_role,
)
from middlewares.auth import ensure_admin
from middlewares.error_handler import AppError
from models.task import Task
from models.user import DEFAULT_ROLE, User
from utils.helpers import utc_now

logger = logging.getLogger(__name__)

USER_NOT_FOUND = 'Usuário não encontrado'
EMAIL_IN_USE = 'Email já cadastrado'
INVALID_CREDENTIALS = 'Credenciais inválidas'
# Placeholder kept from the original API. It is not a credential: no endpoint accepts it.
LOGIN_TOKEN_PREFIX = 'fake-jwt-token-'


def _get_user_or_404(user_id):
    user = User.find_by_id(user_id)
    if not user:
        raise AppError(USER_NOT_FOUND, 404)
    return user


def get_users():
    task_counts = Task.count_by_user()
    result = []
    for user in User.find_all():
        user_data = user.to_dict()
        user_data['task_count'] = task_counts.get(user.id, 0)
        result.append(user_data)
    return jsonify(result), 200


def get_user(user_id):
    user = _get_user_or_404(user_id)
    user_data = user.to_dict()
    user_data['tasks'] = [task.to_dict() for task in Task.find_by_user(user_id)]
    return jsonify(user_data), 200


def create_user():
    data = require_json_object(request.get_json())
    fields = validate_new_user(data)

    if User.find_by_email(fields['email']):
        raise AppError(EMAIL_IN_USE, 409)

    role = validate_role(fields['role'])
    if role != DEFAULT_ROLE:
        # Only an administrator may create a user with elevated privileges.
        ensure_admin()

    user = User(name=fields['name'], email=fields['email'], role=role)
    user.set_password(fields['password'])
    user.save()
    logger.info('Usuário criado: %s', user.id)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = _get_user_or_404(user_id)
    data = require_json_object(request.get_json())

    if 'name' in data:
        user.name = validate_name(data['name'])

    if 'email' in data:
        email = validate_email_format(data['email'])
        existing = User.find_by_email(email)
        if existing and existing.id != user_id:
            raise AppError(EMAIL_IN_USE, 409)
        user.email = email

    if 'password' in data:
        user.set_password(validate_password(data['password'], 'Senha muito curta'))

    if 'role' in data:
        user.role = validate_role(data['role'])

    if 'active' in data:
        user.active = validate_active(data['active'])

    user.save()
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    user.delete_with_tasks()
    logger.info('Usuário deletado: %s', user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    now = utc_now()
    result = []
    for task in Task.find_by_user(user_id):
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': task.is_overdue(now),
        })
    return jsonify(result), 200


def login():
    data = require_json_object(request.get_json())
    email, password = validate_credentials(data)

    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        raise AppError(INVALID_CREDENTIALS, 401)

    if not user.active:
        raise AppError('Usuário inativo', 403)

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': LOGIN_TOKEN_PREFIX + str(user.id)
    }), 200
