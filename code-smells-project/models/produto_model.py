import json

from database import get_db

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIA_PADRAO = "geral"
NOME_TAMANHO_MINIMO = 2
NOME_TAMANHO_MAXIMO = 200

CAMPOS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")


def _to_dict(row):
    return {campo: row[campo] for campo in CAMPOS}


def get_todos_produtos():
    rows = get_db().execute("SELECT * FROM produtos").fetchall()
    return [_to_dict(row) for row in rows]


def get_produto_por_id(produto_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _to_dict(row) if row else None


def get_produtos_por_ids(produto_ids):
    """Return the products found, as a dictionary keyed by id, with one query."""
    ids = list(set(produto_ids))
    if not ids:
        return {}
    # The whole id list travels as one JSON parameter.
    rows = get_db().execute(
        "SELECT * FROM produtos WHERE id IN (SELECT value FROM json_each(?))",
        (json.dumps(ids),),
    ).fetchall()
    return {row["id"]: _to_dict(row) for row in rows}


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
    return cursor.lastrowid


def atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    with db:
        db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )


def deletar_produto(produto_id):
    db = get_db()
    with db:
        db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        padrao = "%" + termo + "%"
        params.extend([padrao, padrao])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max:
        query += " AND preco <= ?"
        params.append(preco_max)

    rows = get_db().execute(query, params).fetchall()
    return [_to_dict(row) for row in rows]


def contar_produtos():
    return get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
