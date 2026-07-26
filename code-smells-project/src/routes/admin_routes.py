from flask import Blueprint
from src.controllers import admin_controller as c

admin_bp = Blueprint("admin", __name__)
admin_bp.add_url_rule("/admin/reset-db", "reset_database", c.reset_database, methods=["POST"])
