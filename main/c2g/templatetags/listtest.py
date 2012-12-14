from django import template

register = template.Library()

@register.filter
def islist(value):
    return isinstance(value,list)

@register.filter
def subOneThenMult(value, arg):
    """Subtracts one from arg then multiplies by value"""
    return (value) * (arg - 1)

