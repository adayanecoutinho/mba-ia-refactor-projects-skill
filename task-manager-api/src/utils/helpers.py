"""Utilitários compartilhados. `process_task_data` já existia no projeto
legado mas nunca era chamada — cada rota reimplementava sua própria
validação manualmente. Agora é reaproveitada pelo task_controller."""
from datetime import datetime
import re


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email))


def parse_date(date_string):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_string, fmt)
        except (ValueError, TypeError):
            continue
    return None


def is_valid_color(color):
    return bool(color and len(color) == 7 and color[0] == "#")


def process_task_data(data, existing_task=None):
    result = {}

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return None, "Título não pode ser vazio"
        if not (3 <= len(title) <= 200):
            return None, "Título deve ter entre 3 e 200 caracteres"
        result["title"] = title

    if "description" in data:
        result["description"] = data["description"]

    if "status" in data:
        valid_statuses = ("pending", "in_progress", "done", "cancelled")
        if data["status"] not in valid_statuses:
            return None, "Status inválido"
        result["status"] = data["status"]

    if "priority" in data:
        try:
            p = int(data["priority"])
        except (TypeError, ValueError):
            return None, "Prioridade inválida"
        if not (1 <= p <= 5):
            return None, "Prioridade deve ser entre 1 e 5"
        result["priority"] = p

    if "due_date" in data:
        if data["due_date"]:
            parsed = parse_date(data["due_date"])
            if not parsed:
                return None, "Data inválida"
            result["due_date"] = parsed
        else:
            result["due_date"] = None

    if "tags" in data:
        tags = data["tags"]
        result["tags"] = ",".join(tags) if isinstance(tags, list) else tags

    return result, None
