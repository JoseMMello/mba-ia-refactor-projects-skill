import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

HTTP_BAD_REQUEST = 400
HTTP_INTERNAL_ERROR = 500
MENSAGEM_ERRO_INTERNO = "Erro interno do servidor"


class AppError(Exception):
    """Expected error, answered to the client with its message and status."""

    def __init__(self, message, status=HTTP_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status = status


def _error_response(message, status):
    return jsonify({"erro": message, "sucesso": False}), status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return _error_response(error.message, error.status)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return _error_response(error.description, error.code)

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Unhandled error")
        return _error_response(MENSAGEM_ERRO_INTERNO, HTTP_INTERNAL_ERROR)
