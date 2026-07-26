from flask import Blueprint
from src.controllers import report_controller as c

report_bp = Blueprint("reports", __name__)
report_bp.add_url_rule("/reports/summary", "summary_report", c.summary_report, methods=["GET"])
report_bp.add_url_rule("/reports/user/<int:user_id>", "user_report", c.user_report, methods=["GET"])
report_bp.add_url_rule("/categories", "get_categories", c.get_categories, methods=["GET"])
report_bp.add_url_rule("/categories", "create_category", c.create_category, methods=["POST"])
report_bp.add_url_rule("/categories/<int:cat_id>", "update_category", c.update_category, methods=["PUT"])
report_bp.add_url_rule("/categories/<int:cat_id>", "delete_category", c.delete_category, methods=["DELETE"])
