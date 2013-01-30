from django import template

register = template.Library()

@register.filter(name='byKey')
def bykey(d, key_name):
    """Return d[key_name] (as opposed to the normal behavior, d['key_name']"""
    try:
        return d[key_name]
    except KeyError:
        return ''

@register.filter(name='uscore2space')
def uscore2space(s):
    """Return s with underscores turned into spaces"""
    return s.replace('_', ' ')
