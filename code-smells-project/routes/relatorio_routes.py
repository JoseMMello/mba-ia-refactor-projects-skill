from flask import Blueprint

from controllers import relatorio_controller

relatorios_bp = Blueprint("relatorios", __name__)

relatorios_bp.add_url_rule("/relatorios/vendas", view_func=relatorio_controller.relatorio_vendas, methods=["GET"])
