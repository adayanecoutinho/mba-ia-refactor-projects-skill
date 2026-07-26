from flask import request, jsonify

from src.config.database import db
from src.models.task import Task
from src.models.user import User
from src.models.category import Category
from src.utils.helpers import process_task_data


def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    return jsonify(task.to_dict()), 200


def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    if not data.get("title"):
        return jsonify({"error": "Título é obrigatório"}), 400

    # Reaproveita `process_task_data`, que já existia em utils/helpers.py
    # mas nunca era chamada — cada rota reimplementava sua própria versão
    # da validação manualmente.
    parsed, error = process_task_data(data)
    if error:
        return jsonify({"error": error}), 400

    if parsed.get("user_id"):
        if not db.session.get(User, parsed["user_id"]):
            return jsonify({"error": "Usuário não encontrado"}), 404
    if parsed.get("category_id"):
        if not db.session.get(Category, parsed["category_id"]):
            return jsonify({"error": "Categoria não encontrada"}), 404

    task = Task(**{**parsed, "user_id": data.get("user_id"), "category_id": data.get("category_id")})
    try:
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao criar task"}), 500


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    parsed, error = process_task_data(data, existing_task=task)
    if error:
        return jsonify({"error": error}), 400

    if "user_id" in data:
        if data["user_id"] and not db.session.get(User, data["user_id"]):
            return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = data["user_id"]
    if "category_id" in data:
        if data["category_id"] and not db.session.get(Category, data["category_id"]):
            return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = data["category_id"]

    for field, value in parsed.items():
        setattr(task, field, value)

    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao atualizar"}), 500


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deletada com sucesso"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao deletar"}), 500


def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%"))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return jsonify([t.to_dict() for t in tasks.all()]), 200


def task_stats():
    total = Task.query.count()
    by_status = {
        status: Task.query.filter_by(status=status).count()
        for status in ("pending", "in_progress", "done", "cancelled")
    }
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    return jsonify({
        "total": total,
        **by_status,
        "overdue": overdue_count,
        "completion_rate": round((by_status["done"] / total) * 100, 2) if total > 0 else 0,
    }), 200
