"""Controllers de pedidos. A regra de negócio pesada (checar estoque,
calcular total) vive em src/models/pedido_model.py; aqui só orquestramos."""
from flask import request, jsonify, current_app

from src.models import pedido_model


def criar_pedido():
    conn = current_app.config["DB_CONNECTION"]
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = pedido_model.criar(conn, usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    current_app.logger.info(
        "Pedido %s criado para usuário %s — notificações (email/sms/push) seriam disparadas aqui via um serviço dedicado.",
        resultado["pedido_id"], usuario_id,
    )

    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    conn = current_app.config["DB_CONNECTION"]
    pedidos = pedido_model.get_por_usuario(conn, usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos_pedidos():
    conn = current_app.config["DB_CONNECTION"]
    pedidos = pedido_model.get_todos(conn)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    conn = current_app.config["DB_CONNECTION"]
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")

    if novo_status not in current_app.config["APP_SETTINGS"].STATUS_PEDIDO_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    pedido_model.atualizar_status(conn, pedido_id, novo_status)
    current_app.logger.info("Pedido %s -> status %s", pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    conn = current_app.config["DB_CONNECTION"]
    relatorio = pedido_model.relatorio_vendas(conn, current_app.config["APP_SETTINGS"])
    return jsonify({"dados": relatorio, "sucesso": True}), 200
