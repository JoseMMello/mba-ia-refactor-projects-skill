from models import pedido_model

# (faturamento acima de, taxa de desconto), from the highest tier to the lowest.
FAIXAS_DESCONTO = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)
CASAS_DECIMAIS = 2


def calcular_desconto(faturamento):
    for limite, taxa in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * taxa
    return 0


def relatorio_vendas():
    resumo = pedido_model.get_resumo_vendas()
    total_pedidos = resumo["total_pedidos"]
    faturamento = resumo["faturamento"]
    desconto = calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, CASAS_DECIMAIS),
        "desconto_aplicavel": round(desconto, CASAS_DECIMAIS),
        "faturamento_liquido": round(faturamento - desconto, CASAS_DECIMAIS),
        "pedidos_pendentes": resumo["pendentes"],
        "pedidos_aprovados": resumo["aprovados"],
        "pedidos_cancelados": resumo["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, CASAS_DECIMAIS) if total_pedidos > 0 else 0,
    }
