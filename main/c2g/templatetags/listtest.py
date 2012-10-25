from django import template

register = template.Library()

@register.filter
def islist(value):
    return isinstance(value,list)