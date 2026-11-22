from flask import jsonify

from middlewares.error_handler import AppError
from models.user import User
from services import report_service

USER_NOT_FOUND = 'Usuário não encontrado'


def summary_report():
    return jsonify(report_service.build_summary_report()), 200


def user_report(user_id):
    user = User.find_by_id(user_id)
    if not user:
        raise AppError(USER_NOT_FOUND, 404)
    return jsonify(report_service.build_user_report(user)), 200
