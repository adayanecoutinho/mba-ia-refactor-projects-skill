"""Acesso a dados de produtos. Toda query é parametrizada (sem concatenação
de string) para eliminar o risco de SQL Injection do código legado."""


def _row_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_todos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_row_to_dict(row) for row in cursor.fetchall()]


def get_por_id(conn, produto_id: int):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return _row_to_dict(row) if row else None


def criar(conn, nome, descricao, preco, estoque, categoria) -> int:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    conn.commit()
    return cursor.lastrowid


def atualizar(conn, produto_id, nome, descricao, preco, estoque, categoria) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    conn.commit()
    return True


def deletar(conn, produto_id) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    return True


def buscar(conn, termo=None, categoria=None, preco_min=None, preco_max=None):
    cursor = conn.cursor()
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor.execute(query, params)
    return [_row_to_dict(row) for row in cursor.fetchall()]


def decrementar_estoque(conn, produto_id, quantidade) -> None:
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id),
    )
