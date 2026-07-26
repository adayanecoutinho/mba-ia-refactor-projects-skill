"""Configuração centralizada. Nenhum segredo hardcoded: tudo lido de
variáveis de ambiente, com defaults seguros apenas para desenvolvimento."""
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    VALID_STATUSES = ("pending", "in_progress", "done", "cancelled")
    VALID_ROLES = ("user", "admin", "manager")
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_PASSWORD_LENGTH = 4
    DEFAULT_PRIORITY = 3
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

    PRIORITY_LABELS = {1: "critical", 2: "high", 3: "medium", 4: "low", 5: "minimal"}
