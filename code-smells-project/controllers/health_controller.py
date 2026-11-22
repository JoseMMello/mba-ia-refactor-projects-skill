from flask import jsonify

from config.settings import settings
from models import pedido_model, produto_model, usuario_model

API_VERSAO = "1.0.0"


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSAO,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produto_model.contar_produtos(),
            "usuarios": usuario_model.contar_usuarios(),
            "pedidos": pedido_model.contar_pedidos(),
        },
        "versao": API_VERSAO,
        "ambiente": settings.AMBIENTE,
    }), 200
