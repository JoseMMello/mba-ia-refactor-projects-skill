import logging

from flask import jsonify, request

from controllers import validators
from middlewares.error_handler import AppError
from models import produto_model

logger = logging.getLogger(__name__)

HTTP_NOT_FOUND = 404


def _get_produto_ou_404(produto_id):
    produto = produto_model.get_produto_por_id(produto_id)
    if not produto:
        raise AppError("Produto não encontrado", HTTP_NOT_FOUND)
    return produto


def listar_produtos():
    produtos = produto_model.get_todos_produtos()
    logger.debug("Listando %s produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = _get_produto_ou_404(produto_id)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    campos = validators.validar_produto(request.get_json(silent=True))
    produto_id = produto_model.criar_produto(*campos)
    logger.info("Produto criado com ID %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    _get_produto_ou_404(produto_id)
    campos = validators.validar_produto(request.get_json(silent=True))
    produto_model.atualizar_produto(produto_id, *campos)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    _get_produto_ou_404(produto_id)
    produto_model.deletar_produto(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = validators.validar_filtro_preco(request.args.get("preco_min"), "preco_min")
    preco_max = validators.validar_filtro_preco(request.args.get("preco_max"), "preco_max")

    resultados = produto_model.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
