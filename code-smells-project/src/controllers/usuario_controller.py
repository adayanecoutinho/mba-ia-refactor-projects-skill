"""Controllers de usuários e autenticação."""
from flask import request, jsonify, current_app

from src.models import usuario_model


def listar_usuarios():
    conn = current_app.config["DB_CONNECTION"]
    usuarios = usuario_model.get_todos(conn)
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(id):
    conn = current_app.config["DB_CONNECTION"]
    usuario = usuario_model.get_por_id(conn, id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar_usuario():
    conn = current_app.config["DB_CONNECTION"]
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    usuario_id = usuario_model.criar(conn, nome, email, senha)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    conn = current_app.config["DB_CONNECTION"]
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = usuario_model.autenticar(conn, email, senha)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
