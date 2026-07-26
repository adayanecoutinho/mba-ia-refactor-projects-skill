"""Acesso a dados de usuários. Queries parametrizadas; a comparação de senha
segue em texto puro apenas para preservar o contrato de dados existente do
projeto legado (seed com senhas em texto puro) — ver README, seção de
achados conhecidos e não corrigidos por estarem fora do escopo de MVC."""


def _row_to_dict(row, incluir_senha=True):
    data = {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
    if incluir_senha:
        data["senha"] = row["senha"]
    return data


def get_todos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_row_to_dict(row) for row in cursor.fetchall()]


def get_por_id(conn, usuario_id: int):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def autenticar(conn, email: str, senha: str):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
        (email, senha),
    )
    row = cursor.fetchone()
    return _row_to_dict(row, incluir_senha=False) if row else None


def criar(conn, nome, email, senha, tipo="cliente") -> int:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha, tipo),
    )
    conn.commit()
    return cursor.lastrowid
