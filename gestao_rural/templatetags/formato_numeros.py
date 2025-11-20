from django import template

register = template.Library()

@register.filter
def formato_br(numero):
    """Formata número no padrão brasileiro: 1.234.567,89"""
    try:
        numero_float = float(numero)
        return f"{numero_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(numero)

@register.filter
def formato_monetario(numero):
    """Formata valor monetário: R$ 1.234.567,89"""
    try:
        numero_float = float(numero)
        return f"R$ {numero_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return f"R$ 0,00"

@register.filter
def formato_numero_inteiro(numero):
    """Formata número inteiro: 1.234"""
    try:
        numero_int = int(float(numero))
        return f"{numero_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(numero)

@register.filter
def formato_decimal(numero):
    """Formata decimal: 1.234,56"""
    try:
        numero_float = float(numero)
        return f"{numero_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return str(numero)

