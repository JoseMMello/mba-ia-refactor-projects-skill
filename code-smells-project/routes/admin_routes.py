from flask import Blueprint

from controllers import admin_controller
from middlewares.auth import require_admin

admin_bp = Blueprint("admin", __name__)

admin_bp.add_url_rule(
    "/admin/reset-db",
    view_func=require_admin(admin_controller.reset_database),
    methods=["POST"],
)
