from django import template
from courses.exams.views import compute_penalties
import math
import datetime

register = template.Library()

@register.filter
def islist(value):
    return isinstance(value,list)

@register.filter
def subOneThenMult(value, arg):
    """Subtracts one from arg then multiplies by value"""
    return (value) * (arg - 1)

@register.filter
def sub(value, arg):
    """Subtracts arg from value"""
    return (value) - (arg)

@register.filter
def getActualLatePenaltyPercent(record, exam):
    """combines the constant and daily late penalties into one number"""
    days_late = record.days_late(grace_period=exam.grace_period)
    max_possible = compute_penalties(100.0, 1, 0, record.late, exam.late_penalty, late_days=days_late, daily_late_penalty=exam.daily_late_penalty)
    return round(100.0 - max_possible, 1)