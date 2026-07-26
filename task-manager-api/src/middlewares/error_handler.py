from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception(e)
        return jsonify({"error": "Erro interno do servidor"}), 500
