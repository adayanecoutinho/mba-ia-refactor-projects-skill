from flask import Blueprint
from src.controllers import sistema_controller as c

sistema_bp = Blueprint("sistema", __name__)
sistema_bp.add_url_rule("/", "index", c.index, methods=["GET"])
sistema_bp.add_url_rule("/health", "health_check", c.health_check, methods=["GET"])
