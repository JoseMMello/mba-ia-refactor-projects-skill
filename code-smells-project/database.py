import logging
import secrets
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

from config.settings import settings

logger = logging.getLogger(__name__)

SCHEMA = """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    );
"""

SEED_PRODUTOS = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# (nome, email, tipo). The passwords come from the configuration.
SEED_USUARIOS = [
    ("Admin", "admin@loja.com", "admin"),
    ("João Silva", "joao@email.com", "cliente"),
    ("Maria Santos", "maria@email.com", "cliente"),
]


def _connect():
    connection = sqlite3.connect(settings.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_db():
    """Return the connection of the current request, opening it on first use."""
    if "db" not in g:
        g.db = _connect()
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def _seed_password(configured, tipo):
    if configured:
        return configured
    logger.warning(
        "No seed password configured for sample users of type '%s'; "
        "they get a random password and cannot log in. "
        "Set SEED_ADMIN_PASSWORD and SEED_USER_PASSWORD before the first boot.",
        tipo,
    )
    return secrets.token_urlsafe(32)


def _seed(connection):
    if connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] != 0:
        return

    connection.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        SEED_PRODUTOS,
    )

    senhas = {
        "admin": _seed_password(settings.SEED_ADMIN_PASSWORD, "admin"),
        "cliente": _seed_password(settings.SEED_USER_PASSWORD, "cliente"),
    }
    connection.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        [
            (nome, email, generate_password_hash(senhas[tipo]), tipo)
            for nome, email, tipo in SEED_USUARIOS
        ],
    )


def init_db():
    """Create the schema and, for an empty database, the sample data."""
    connection = _connect()
    try:
        connection.executescript(SCHEMA)
        _seed(connection)
        connection.commit()
    finally:
        connection.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    init_db()
