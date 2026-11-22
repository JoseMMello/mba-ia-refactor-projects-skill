import re

from middlewares.error_handler import AppError
from models import pedido_model, produto_model

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _require_body(dados):
    if not isinstance(dados, dict) or not dados:
        raise AppError("Dados inválidos")


def validar_produto(dados):
    """Validate a product body, for create and update, and return its fields."""
    _require_body(dados)
    if "nome" not in dados:
        raise AppError("Nome é obrigatório")
    if "preco" not in dados:
        raise AppError("Preço é obrigatório")
    if "estoque" not in dados:
        raise AppError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", produto_model.CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise AppError("Nome inválido")
    if not _is_number(preco):
        raise AppError("Preço inválido")
    if not _is_integer(estoque):
        raise AppError("Estoque inválido")
    if not isinstance(descricao, str):
        raise AppError("Descrição inválida")

    if preco < 0:
        raise AppError("Preço não pode ser negativo")
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo")
    if len(nome) < produto_model.NOME_TAMANHO_MINIMO:
        raise AppError("Nome muito curto")
    if len(nome) > produto_model.NOME_TAMANHO_MAXIMO:
        raise AppError("Nome muito longo")
    if categoria not in produto_model.CATEGORIAS_VALIDAS:
        raise AppError("Categoria inválida. Válidas: " + str(produto_model.CATEGORIAS_VALIDAS))

    return nome, descricao, preco, estoque, categoria


def validar_filtro_preco(valor, nome_parametro):
    """Convert an optional price filter from the query string."""
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise AppError(nome_parametro + " inválido") from None


def validar_usuario(dados):
    _require_body(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise AppError("Nome, email e senha são obrigatórios")
    if not all(isinstance(valor, str) for valor in (nome, email, senha)):
        raise AppError("Nome, email e senha devem ser texto")
    if not EMAIL_PATTERN.match(email):
        raise AppError("Email inválido")

    return nome, email, senha


def validar_login(dados):
    if not isinstance(dados, dict):
        dados = {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise AppError("Email e senha são obrigatórios")
    if not isinstance(email, str) or not isinstance(senha, str):
        raise AppError("Email e senha devem ser texto")

    return email, senha


def validar_pedido(dados):
    _require_body(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise AppError("Usuario ID é obrigatório")
    if not _is_integer(usuario_id):
        raise AppError("Usuario ID inválido")
    if not isinstance(itens, list) or len(itens) == 0:
        raise AppError("Pedido deve ter pelo menos 1 item")

    for item in itens:
        if (
            not isinstance(item, dict)
            or not _is_integer(item.get("produto_id"))
            or not _is_integer(item.get("quantidade"))
            or item["quantidade"] <= 0
        ):
            raise AppError("Item inválido: produto_id e quantidade maior que zero são obrigatórios")

    return usuario_id, itens


def validar_status(dados):
    novo_status = dados.get("status", "") if isinstance(dados, dict) else ""
    if novo_status not in pedido_model.STATUS_VALIDOS:
        raise AppError("Status inválido")
    return novo_status
