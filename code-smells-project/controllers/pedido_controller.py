from flask import jsonify, request

from controllers import validators
from models import pedido_model
from services import pedido_service


def criar_pedido():
    usuario_id, itens = validators.validar_pedido(request.get_json(silent=True))
    resultado = pedido_service.criar_pedido(usuario_id, itens)
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_model.get_pedidos(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    pedidos = pedido_model.get_pedidos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    novo_status = validators.validar_status(request.get_json(silent=True))
    pedido_service.atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
