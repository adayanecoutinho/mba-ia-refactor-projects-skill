"""Composition root: monta a aplicação Flask, registra config, banco,
middlewares e rotas. Não contém lógica de negócio nem definição de rotas
inline (ao contrário do app.py legado, que fazia tudo isso junto)."""
from flask import Flask
from flask_cors import CORS

from src.config.settings import Config
from src.config.database import create_connection, init_schema
from src.middlewares.error_handler import register_error_handlers
from src.routes.produto_routes import produto_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.pedido_routes import pedido_bp, relatorio_bp
from src.routes.sistema_routes import sistema_bp
from src.routes.admin_routes import admin_bp


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    conn = create_connection(app.config["DATABASE_PATH"])
    init_schema(conn)
    app.config["DB_CONNECTION"] = conn
    app.config["APP_SETTINGS"] = config_class

    register_error_handlers(app)

    app.register_blueprint(sistema_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{app.config['PORT']}")
    print("=" * 50)
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
