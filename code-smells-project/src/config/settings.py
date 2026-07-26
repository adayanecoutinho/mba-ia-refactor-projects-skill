"""Configuração centralizada da aplicação. Nunca hardcode segredos aqui:
todos os valores sensíveis vêm de variáveis de ambiente, com defaults
seguros apenas para desenvolvimento local."""
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    CATEGORIAS_VALIDAS = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
    STATUS_PEDIDO_VALIDOS = ("pendente", "aprovado", "enviado", "entregue", "cancelado")

    # Faixas de desconto do relatório de vendas (antes eram "magic numbers" soltos em models.py)
    DESCONTO_FAIXA_ALTA = (10_000, 0.10)
    DESCONTO_FAIXA_MEDIA = (5_000, 0.05)
    DESCONTO_FAIXA_BAIXA = (1_000, 0.02)
