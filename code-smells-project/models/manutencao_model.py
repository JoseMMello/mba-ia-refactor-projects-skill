from database import get_db


def limpar_dados():
    """Delete the rows of every table in one transaction."""
    db = get_db()
    with db:  # commits at the end, rolls back if any step fails
        db.execute("DELETE FROM itens_pedido")
        db.execute("DELETE FROM pedidos")
        db.execute("DELETE FROM produtos")
        db.execute("DELETE FROM usuarios")
