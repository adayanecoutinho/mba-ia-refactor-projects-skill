"""Endpoints administrativos. O endpoint legado `/admin/query` (que
executava SQL arbitrário vindo do corpo da requisição) foi removido nesta
refatoração: era, por definição, a própria vulnerabilidade de SQL
Injection apontada no relatório de auditoria (CRITICAL) — não existe forma
de "corrigi-lo" mantendo seu contrato original, então ele não foi
recriado. Ver README, seção Resultados, para detalhes."""
from flask import jsonify, current_app


def reset_database():
    conn = current_app.config["DB_CONNECTION"]
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    conn.commit()
    current_app.logger.warning("Banco de dados resetado via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
