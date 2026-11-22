import logging

from flask import jsonify

from models import manutencao_model

logger = logging.getLogger(__name__)


def reset_database():
    manutencao_model.limpar_dados()
    logger.warning("Banco de dados resetado")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
