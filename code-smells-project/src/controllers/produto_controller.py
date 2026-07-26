"""Controllers de produtos: orquestram validação + chamada ao model,
formatam a resposta HTTP. Nenhuma query SQL vive aqui."""
from flask import request, jsonify, current_app

from src.models import produto_model


def _validar_payload(dados, config, parcial=False):
    if not dados:
        return "Dados inválidos"
    obrigatorios = () if parcial else ("nome", "preco", "estoque")
    for campo in obrigatorios:
        if campo not in dados:
            return f"{campo.capitalize()} é obrigatório"

    if "preco" in dados and dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if "estoque" in dados and dados["estoque"] < 0:
        return "Estoque não pode ser negativo"
    if "nome" in dados:
        if len(dados["nome"]) < 2:
            return "Nome muito curto"
        if len(dados["nome"]) > 200:
            return "Nome muito longo"
    if "categoria" in dados and dados["categoria"] not in config.CATEGORIAS_VALIDAS:
        return f"Categoria inválida. Válidas: {list(config.CATEGORIAS_VALIDAS)}"
    return None


def listar_produtos():
    conn = current_app.config["DB_CONNECTION"]
    produtos = produto_model.get_todos(conn)
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    conn = current_app.config["DB_CONNECTION"]
    produto = produto_model.get_por_id(conn, id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def buscar_produtos():
    conn = current_app.config["DB_CONNECTION"]
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    preco_min = float(preco_min) if preco_min else None
    preco_max = float(preco_max) if preco_max else None

    resultados = produto_model.buscar(conn, termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def criar_produto():
    conn = current_app.config["DB_CONNECTION"]
    dados = request.get_json(silent=True)
    erro = _validar_payload(dados, current_app.config["APP_SETTINGS"])
    if erro:
        return jsonify({"erro": erro}), 400

    produto_id = produto_model.criar(
        conn,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    conn = current_app.config["DB_CONNECTION"]
    if not produto_model.get_por_id(conn, id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json(silent=True)
    erro = _validar_payload(dados, current_app.config["APP_SETTINGS"])
    if erro:
        return jsonify({"erro": erro}), 400

    produto_model.atualizar(
        conn,
        id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    conn = current_app.config["DB_CONNECTION"]
    if not produto_model.get_por_id(conn, id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_model.deletar(conn, id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
