from django import template

register = template.Library()


@register.filter
def index(lista, i):
    """Retorna o item de índice i de uma lista"""
    try:
        return lista[int(i)]
    except (IndexError, ValueError, TypeError):
        return ""
