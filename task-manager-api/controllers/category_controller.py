from flask import jsonify, request

from controllers.validators.category_validator import validate_category
from controllers.validators.common import require_json_object
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task

CATEGORY_NOT_FOUND = 'Categoria não encontrada'


def _get_category_or_404(category_id):
    category = Category.find_by_id(category_id)
    if not category:
        raise AppError(CATEGORY_NOT_FOUND, 404)
    return category


def get_categories():
    task_counts = Task.count_by_category()
    result = []
    for category in Category.find_all():
        category_data = category.to_dict()
        category_data['task_count'] = task_counts.get(category.id, 0)
        result.append(category_data)
    return jsonify(result), 200


def create_category():
    data = require_json_object(request.get_json())
    category = Category(**validate_category(data, creating=True))
    category.save()
    return jsonify(category.to_dict()), 201


def update_category(category_id):
    category = _get_category_or_404(category_id)
    # An empty object is accepted here, as in the original API: nothing changes.
    data = require_json_object(request.get_json(), allow_empty=True)
    for field, value in validate_category(data, creating=False).items():
        setattr(category, field, value)
    category.save()
    return jsonify(category.to_dict()), 200


def delete_category(category_id):
    category = _get_category_or_404(category_id)
    category.delete()
    return jsonify({'message': 'Categoria deletada'}), 200
