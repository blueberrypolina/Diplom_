from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(str(key), [])

@register.filter
def div(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0