from flask import Blueprint

from controllers import pedido_controller

pedidos_bp = Blueprint("pedidos", __name__)

pedidos_bp.add_url_rule("/pedidos", view_func=pedido_controller.criar_pedido, methods=["POST"])
pedidos_bp.add_url_rule("/pedidos", view_func=pedido_controller.listar_todos_pedidos, methods=["GET"])
pedidos_bp.add_url_rule("/pedidos/usuario/<int:usuario_id>", view_func=pedido_controller.listar_pedidos_usuario, methods=["GET"])
pedidos_bp.add_url_rule("/pedidos/<int:pedido_id>/status", view_func=pedido_controller.atualizar_status_pedido, methods=["PUT"])
