from controllers.validators.common import is_integer
from middlewares.error_handler import AppError
from models.task import (
    DEFAULT_PRIORITY, MAX_PRIORITY, MAX_TITLE_LENGTH, MIN_PRIORITY, MIN_TITLE_LENGTH,
    STATUS_PENDING, TAG_SEPARATOR, TASK_STATUSES,
)
from utils.helpers import parse_date

CREATE_DATE_ERROR = 'Formato de data inválido. Use YYYY-MM-DD'
UPDATE_DATE_ERROR = 'Formato de data inválido'


def _validate_title(title, required):
    if required and not title:
        raise AppError('Título é obrigatório')
    if not isinstance(title, str):
        raise AppError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise AppError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise AppError('Título muito longo')
    return title


def _validate_description(description):
    if description is not None and not isinstance(description, str):
        raise AppError('Descrição inválida')
    return description


def _validate_status(status):
    if not isinstance(status, str) or status not in TASK_STATUSES:
        raise AppError('Status inválido')
    return status


def _validate_priority(priority):
    if not is_integer(priority):
        raise AppError('Prioridade inválida')
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise AppError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return priority


def validate_reference(value, error_message):
    """Checks the type of a user_id or category_id received in the body."""
    if value is not None and not is_integer(value):
        raise AppError(error_message)
    return value


def validate_task_fields(data, creating):
    """Validates title, description, status and priority. Returns only the fields to set."""
    fields = {}
    if creating:
        fields['title'] = _validate_title(data.get('title'), required=True)
        fields['description'] = _validate_description(data.get('description', ''))
        fields['status'] = _validate_status(data.get('status', STATUS_PENDING))
        fields['priority'] = _validate_priority(data.get('priority', DEFAULT_PRIORITY))
        return fields

    if 'title' in data:
        fields['title'] = _validate_title(data['title'], required=False)
    if 'description' in data:
        fields['description'] = _validate_description(data['description'])
    if 'status' in data:
        fields['status'] = _validate_status(data['status'])
    if 'priority' in data:
        fields['priority'] = _validate_priority(data['priority'])
    return fields


def _join_tags(tags):
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise AppError('Tags inválidas')
        return TAG_SEPARATOR.join(tags)
    if tags is not None and not isinstance(tags, str):
        raise AppError('Tags inválidas')
    return tags


def validate_task_schedule(data, creating):
    """Validates due_date and tags. Returns only the fields to set."""
    fields = {}
    date_error = CREATE_DATE_ERROR if creating else UPDATE_DATE_ERROR

    if data.get('due_date'):
        due_date = parse_date(data['due_date'])
        if due_date is None:
            raise AppError(date_error)
        fields['due_date'] = due_date
    elif 'due_date' in data and not creating:
        fields['due_date'] = None

    if creating:
        if data.get('tags'):
            fields['tags'] = _join_tags(data['tags'])
    elif 'tags' in data:
        fields['tags'] = _join_tags(data['tags'])
    return fields


def parse_integer_filter(raw_value, name):
    """Converts an optional query string filter to int, or None when it was not sent."""
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError:
        raise AppError(f'Parâmetro {name} inválido')
