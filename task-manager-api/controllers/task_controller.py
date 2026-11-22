import logging

from flask import jsonify, request

from controllers.validators.common import require_json_object
from controllers.validators.task_validator import (
    parse_integer_filter, validate_reference, validate_task_fields, validate_task_schedule,
)
from middlewares.error_handler import AppError
from models.category import Category
from models.task import STATUS_DONE, TASK_STATUSES, Task
from models.user import User
from utils.helpers import calculate_percentage, utc_now

logger = logging.getLogger(__name__)

TASK_NOT_FOUND = 'Task não encontrada'
USER_NOT_FOUND = 'Usuário não encontrado'
CATEGORY_NOT_FOUND = 'Categoria não encontrada'


def _get_task_or_404(task_id):
    task = Task.find_by_id(task_id)
    if not task:
        raise AppError(TASK_NOT_FOUND, 404)
    return task


def _serialize_with_overdue(task, now):
    task_data = task.to_dict()
    task_data['overdue'] = task.is_overdue(now)
    return task_data


def _validate_owner_and_category(data):
    """Checks that the user and the category named in the body exist. Returns the fields to set."""
    fields = {}
    if 'user_id' in data:
        user_id = validate_reference(data['user_id'], 'Usuário inválido')
        if user_id and not User.find_by_id(user_id):
            raise AppError(USER_NOT_FOUND, 404)
        fields['user_id'] = user_id
    if 'category_id' in data:
        category_id = validate_reference(data['category_id'], 'Categoria inválida')
        if category_id and not Category.find_by_id(category_id):
            raise AppError(CATEGORY_NOT_FOUND, 404)
        fields['category_id'] = category_id
    return fields


def _read_task_fields(data, creating):
    fields = validate_task_fields(data, creating)
    fields.update(_validate_owner_and_category(data))
    fields.update(validate_task_schedule(data, creating))
    return fields


def get_tasks():
    now = utc_now()
    result = []
    for task in Task.find_all_with_relations():
        task_data = _serialize_with_overdue(task, now)
        task_data['user_name'] = task.user.name if task.user else None
        task_data['category_name'] = task.category.name if task.category else None
        result.append(task_data)
    return jsonify(result), 200


def get_task(task_id):
    task = _get_task_or_404(task_id)
    return jsonify(_serialize_with_overdue(task, utc_now())), 200


def create_task():
    data = require_json_object(request.get_json())
    task = Task(**_read_task_fields(data, creating=True))
    task.save()
    logger.info('Task criada: %s - %s', task.id, task.title)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = _get_task_or_404(task_id)
    data = require_json_object(request.get_json())
    for field, value in _read_task_fields(data, creating=False).items():
        setattr(task, field, value)
    task.touch()
    task.save()
    logger.info('Task atualizada: %s', task.id)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    task.delete()
    logger.info('Task deletada: %s', task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    tasks = Task.search(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=parse_integer_filter(request.args.get('priority', ''), 'priority'),
        user_id=parse_integer_filter(request.args.get('user_id', ''), 'user_id'),
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    total = Task.count_all()
    counts = Task.count_by_status()
    now = utc_now()
    overdue = sum(1 for task in Task.find_with_due_date() if task.is_overdue(now))

    stats = {'total': total}
    for status in TASK_STATUSES:
        stats[status] = counts.get(status, 0)
    stats['overdue'] = overdue
    stats['completion_rate'] = calculate_percentage(counts.get(STATUS_DONE, 0), total)
    return jsonify(stats), 200
