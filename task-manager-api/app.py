"""Composition root: monta a aplicação Flask, registra config, banco,
middlewares e blueprints. Não contém lógica de negócio."""
from flask import Flask
from flask_cors import CORS

from src.config.settings import Config
from src.config.database import db
from src.middlewares.error_handler import register_error_handlers
from src.routes.task_routes import task_bp
from src.routes.user_routes import user_bp
from src.routes.report_routes import report_bp


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["APP_SETTINGS"] = config_class
    CORS(app)

    db.init_app(app)

    register_error_handlers(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route("/health")
    def health():
        import datetime
        return {"status": "ok", "timestamp": str(datetime.datetime.now())}

    @app.route("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host=app.config["HOST"], port=app.config["PORT"])
