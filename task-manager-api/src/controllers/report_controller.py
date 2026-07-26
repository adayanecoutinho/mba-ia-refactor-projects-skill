from collections import defaultdict
from datetime import datetime, timedelta

from flask import request, jsonify

from src.config.database import db
from src.models.task import Task
from src.models.user import User
from src.models.category import Category


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    by_status = {
        status: Task.query.filter_by(status=status).count()
        for status in ("pending", "in_progress", "done", "cancelled")
    }
    by_priority_label = {1: "critical", 2: "high", 3: "medium", 4: "low", 5: "minimal"}
    by_priority = {
        by_priority_label[p]: Task.query.filter_by(priority=p).count() for p in range(1, 6)
    }

    all_tasks = Task.query.all()
    overdue_list = [
        {
            "id": t.id,
            "title": t.title,
            "due_date": str(t.due_date),
            "days_overdue": (datetime.utcnow() - t.due_date).days,
        }
        for t in all_tasks
        if t.is_overdue()
    ]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done", Task.updated_at >= seven_days_ago
    ).count()

    # Produtividade por usuário resolvida com uma única leitura de `all_tasks`
    # agrupada em memória, em vez de 1 query `Task.query.filter_by(user_id=...)`
    # por usuário (N+1 do código legado).
    tasks_by_user = defaultdict(list)
    for t in all_tasks:
        if t.user_id:
            tasks_by_user[t.user_id].append(t)

    user_stats = []
    for u in User.query.all():
        user_tasks = tasks_by_user.get(u.id, [])
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == "done")
        user_stats.append({
            "user_id": u.id,
            "user_name": u.name,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": round((completed / total) * 100, 2) if total > 0 else 0,
        })

    report = {
        "generated_at": str(datetime.utcnow()),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": by_status,
        "tasks_by_priority": by_priority,
        "overdue": {"count": len(overdue_list), "tasks": overdue_list},
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }
    return jsonify(report), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    by_status = defaultdict(int)
    overdue = 0
    high_priority = 0
    for t in tasks:
        by_status[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    report = {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": by_status["done"],
            "pending": by_status["pending"],
            "in_progress": by_status["in_progress"],
            "cancelled": by_status["cancelled"],
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": round((by_status["done"] / total) * 100, 2) if total > 0 else 0,
        },
    }
    return jsonify(report), 200


def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data["task_count"] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json(silent=True)
    if not data or not data.get("name"):
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = Category()
    category.name = data["name"]
    category.description = data.get("description", "")
    category.color = data.get("color", "#000000")

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao criar categoria"}), 500


def update_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({"error": "Categoria não encontrada"}), 404

    data = request.get_json(silent=True) or {}
    for field in ("name", "description", "color"):
        if field in data:
            setattr(cat, field, data[field])

    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao atualizar"}), 500


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({"error": "Categoria não encontrada"}), 404
    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({"message": "Categoria deletada"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Erro ao deletar"}), 500
