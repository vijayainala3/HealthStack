from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the argument.
    Usage: {{ quantity|multiply:price }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
