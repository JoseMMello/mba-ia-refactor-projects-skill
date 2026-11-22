from middlewares.error_handler import AppError
from models.category import DEFAULT_COLOR
from utils.helpers import is_valid_color

NAME_REQUIRED_MESSAGE = 'Nome é obrigatório'


def _validate_name(name):
    if not name:
        raise AppError(NAME_REQUIRED_MESSAGE)
    if not isinstance(name, str):
        raise AppError('Nome inválido')
    return name


def _validate_description(description):
    if description is not None and not isinstance(description, str):
        raise AppError('Descrição inválida')
    return description


def _validate_color(color):
    if not is_valid_color(color):
        raise AppError('Cor inválida. Use o formato #RRGGBB')
    return color


def validate_category(data, creating):
    """Returns only the category fields to set."""
    fields = {}
    if creating:
        fields['name'] = _validate_name(data.get('name'))
        fields['description'] = _validate_description(data.get('description', ''))
        fields['color'] = _validate_color(data.get('color', DEFAULT_COLOR))
        return fields

    if 'name' in data:
        fields['name'] = _validate_name(data['name'])
    if 'description' in data:
        fields['description'] = _validate_description(data['description'])
    if 'color' in data:
        fields['color'] = _validate_color(data['color'])
    return fields
