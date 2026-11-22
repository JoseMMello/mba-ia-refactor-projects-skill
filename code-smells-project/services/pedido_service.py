import logging

from middlewares.error_handler import AppError
from models import pedido_model, produto_model

logger = logging.getLogger(__name__)


def criar_pedido(usuario_id, itens):
    """Check stock, compute the total and create the order."""
    produtos = produto_model.get_produtos_por_ids(item["produto_id"] for item in itens)

    total = 0
    itens_pedido = []
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise AppError("Produto " + str(item["produto_id"]) + " não encontrado")
        if produto["estoque"] < item["quantidade"]:
            raise AppError("Estoque insuficiente para " + produto["nome"])
        total = total + (produto["preco"] * item["quantidade"])
        itens_pedido.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": produto["preco"],
        })

    pedido_id = pedido_model.criar_pedido(usuario_id, total, itens_pedido)
    _notificar_pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    pedido_model.atualizar_status_pedido(pedido_id, novo_status)

    if novo_status == pedido_model.STATUS_APROVADO:
        logger.info("Notificação: pedido %s foi aprovado, preparar envio", pedido_id)
    if novo_status == pedido_model.STATUS_CANCELADO:
        logger.info("Notificação: pedido %s cancelado, devolver estoque", pedido_id)


def _notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("Enviando e-mail: pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("Enviando SMS: pedido %s recebido", pedido_id)
    logger.info("Enviando push: novo pedido %s recebido pelo sistema", pedido_id)
