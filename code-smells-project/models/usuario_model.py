import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db

TIPO_PADRAO = "cliente"
PREFIXOS_HASH = ("scrypt:", "pbkdf2:")

# The password column is never selected for responses.
CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")
CAMPOS_LOGIN = ("id", "nome", "email", "tipo")


def _to_dict(row, campos=CAMPOS_PUBLICOS):
    return {campo: row[campo] for campo in campos}


def get_todos_usuarios():
    rows = get_db().execute("SELECT id, nome, email, tipo, criado_em FROM usuarios").fetchall()
    return [_to_dict(row) for row in rows]


def get_usuario_por_id(usuario_id):
    row = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return _to_dict(row) if row else None


def criar_usuario(nome, email, senha, tipo=TIPO_PADRAO):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), tipo),
        )
    return cursor.lastrowid


def _senha_confere(db, row, senha):
    armazenada = row["senha"] or ""
    if armazenada.startswith(PREFIXOS_HASH):
        return check_password_hash(armazenada, senha)

    # Row created before passwords were hashed: compare it once and store the hash.
    if not hmac.compare_digest(armazenada.encode("utf-8"), senha.encode("utf-8")):
        return False
    with db:
        db.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (generate_password_hash(senha), row["id"]),
        )
    return True


def autenticar(email, senha):
    """Return the user when the e-mail and password match, otherwise None."""
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchall()
    for row in rows:
        if _senha_confere(db, row, senha):
            return _to_dict(row, CAMPOS_LOGIN)
    return None


def contar_usuarios():
    return get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
