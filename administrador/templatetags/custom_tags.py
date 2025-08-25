from django import template
from datetime import datetime

register = template.Library()


@register.filter
def index(lista, i):
    """Retorna o item de índice i de uma lista"""
    try:
        return lista[int(i)]
    except (IndexError, ValueError, TypeError):
        return ""


@register.filter
def get_item(d, key):
    return d.get(key)


@register.filter
def to_float(value):
    try:
        float(value)
    except (ValueError, TypeError):
        return value


@register.filter
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return to_float(value)


@register.filter
def format_date(value, fmt="%d/%m/%Y"):
    if not value:
        return ""
    try:
        if isinstance(value, str):  # se já for string no formato ISO
            value = datetime.fromisoformat(value.replace("Z", ""))
        return value.strftime(fmt)
    except Exception:
        return value


@register.filter
def todas_ou_valor(value):
    return "Todas" if str(value) == "0" else value
