from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Divide un string por el separador dado. Uso: {{ "a,b,c"|split:"," }}"""
    return value.split(arg)