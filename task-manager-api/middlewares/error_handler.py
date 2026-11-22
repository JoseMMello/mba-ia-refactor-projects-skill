import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

INTERNAL_ERROR_MESSAGE = 'Erro interno'


class AppError(Exception):
    """Expected error of a request. The message is safe to send to the client."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception('Unhandled error')
        return jsonify({'error': INTERNAL_ERROR_MESSAGE}), 500
