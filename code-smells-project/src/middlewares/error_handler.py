"""Tratamento de erro centralizado: substitui os try/except repetidos que
existiam em cada handler do controllers.py legado."""
from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": str(getattr(e, "description", "Requisição inválida")), "sucesso": False}), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception(e)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
