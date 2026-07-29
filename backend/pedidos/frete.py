from decimal import Decimal

FRETE_BASE = Decimal('10.00')
PRECO_POR_KG = Decimal('2.50')
VALOR_MINIMO_FRETE_GRATIS = Decimal('150.00')

def calcular_frete(peso_total_kg, valor_compra=None):
    if peso_total_kg <= 0:
        return Decimal('0.00')

    if valor_compra is not None and valor_compra >= VALOR_MINIMO_FRETE_GRATIS:
        return Decimal('0.00')

    frete = FRETE_BASE + (Decimal(str(peso_total_kg)) * PRECO_POR_KG)
    return frete.quantize(Decimal('0.01'))
