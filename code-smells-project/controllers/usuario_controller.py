import logging

from flask import jsonify, request

from controllers import validators
from middlewares.error_handler import AppError
from models import usuario_model

logger = logging.getLogger(__name__)

HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404


def listar_usuarios():
    usuarios = usuario_model.get_todos_usuarios()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_usuario_por_id(usuario_id)
    if not usuario:
        raise AppError("Usuário não encontrado", HTTP_NOT_FOUND)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    nome, email, senha = validators.validar_usuario(request.get_json(silent=True))
    usuario_id = usuario_model.criar_usuario(nome, email, senha)
    logger.info("Usuário criado com ID %s", usuario_id)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    email, senha = validators.validar_login(request.get_json(silent=True))
    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        logger.info("Login falhou")
        raise AppError("Email ou senha inválidos", HTTP_UNAUTHORIZED)

    logger.info("Login bem-sucedido para usuario %s", usuario["id"])
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
