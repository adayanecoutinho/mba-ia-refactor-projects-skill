import re

from flask import request, jsonify, current_app

from src.config.database import db
from src.models.user import User
from src.models.task import Task
from src.services.auth_service import issue_token

EMAIL_RE = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"


def get_users():
    users = User.query.all()
    result = []
    for u in users:
        data = u.to_dict()
        data["task_count"] = len(u.tasks)
        result.append(data)
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data["tasks"] = [t.to_dict(include_relations=False) for t in tasks]
    return jsonify(data), 200


def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400
    if not password:
        return jsonify({"error": "Senha é obrigatória"}), 400
    if not re.match(EMAIL_RE, email):
        return jsonify({"error": "Email inválido"}), 400
    if len(password) < current_app.config["APP_SETTINGS"].MIN_PASSWORD_LENGTH:
        return jsonify({"error": "Senha deve ter no mínimo 4 caracteres"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email já cadastrado"}), 409
    if role not in current_app.config["APP_SETTINGS"].VALID_ROLES:
        return jsonify({"error": "Role inválido"}), 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao criar usuário"}), 500


def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        if not re.match(EMAIL_RE, data["email"]):
            return jsonify({"error": "Email inválido"}), 400
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = data["email"]
    if "password" in data:
        if len(data["password"]) < current_app.config["APP_SETTINGS"].MIN_PASSWORD_LENGTH:
            return jsonify({"error": "Senha muito curta"}), 400
        user.set_password(data["password"])
    if "role" in data:
        if data["role"] not in current_app.config["APP_SETTINGS"].VALID_ROLES:
            return jsonify({"error": "Role inválido"}), 400
        user.role = data["role"]
    if "active" in data:
        user.active = data["active"]

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao atualizar"}), 500


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    for t in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(t)

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao deletar"}), 500


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict(include_relations=False) for t in tasks]), 200


def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401
    if not user.active:
        return jsonify({"error": "Usuário inativo"}), 403

    token = issue_token(current_app.config["SECRET_KEY"], user.id)
    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": token,
    }), 200
