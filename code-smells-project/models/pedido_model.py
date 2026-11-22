from database import get_db

STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_VALIDOS = [STATUS_PENDENTE, STATUS_APROVADO, STATUS_ENVIADO, STATUS_ENTREGUE, STATUS_CANCELADO]

PRODUTO_NOME_DESCONHECIDO = "Desconhecido"


def criar_pedido(usuario_id, total, itens):
    """Insert the order, its items and the stock changes in one transaction.

    Each item has produto_id, quantidade and preco_unitario.
    """
    db = get_db()
    with db:  # commits at the end, rolls back if any step fails
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid
        db.executemany(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            [
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
                for item in itens
            ],
        )
        db.executemany(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            [(item["quantidade"], item["produto_id"]) for item in itens],
        )
    return pedido_id


def get_pedidos(usuario_id=None):
    """Return the orders with their items, for one user or for all, with one query."""
    query = """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
               pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
    params = []
    if usuario_id is not None:
        query += " WHERE p.usuario_id = ?"
        params.append(usuario_id)
    query += " ORDER BY p.id, i.id"

    pedidos = {}
    for row in get_db().execute(query, params).fetchall():
        pedido = pedidos.setdefault(row["id"], {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        })
        if row["item_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or PRODUTO_NOME_DESCONHECIDO,
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    with db:
        db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))


def get_resumo_vendas():
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """,
        (STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO),
    ).fetchone()
    return dict(row)


def contar_pedidos():
    return get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
