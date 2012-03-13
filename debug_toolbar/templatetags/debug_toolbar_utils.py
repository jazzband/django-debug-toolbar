
from django import template
from django.utils.numberformat import format

register = template.Library()


@register.filter
def dotted_number(number):
    number = float(number)
    return format(number, '.', 6)

