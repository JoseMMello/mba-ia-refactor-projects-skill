from routes.admin_routes import admin_bp
from routes.health_routes import health_bp
from routes.pedido_routes import pedidos_bp
from routes.produto_routes import produtos_bp
from routes.relatorio_routes import relatorios_bp
from routes.usuario_routes import usuarios_bp

BLUEPRINTS = (produtos_bp, usuarios_bp, pedidos_bp, relatorios_bp, health_bp, admin_bp)


def register_routes(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
