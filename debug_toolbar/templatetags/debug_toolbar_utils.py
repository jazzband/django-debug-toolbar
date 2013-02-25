#coding=utf-8
from __future__ import unicode_literals

from django import template
from django.utils.numberformat import format

register = template.Library()


@register.filter
def dotted_number(number):
    number = float(number)
    return format(number, '.', 6)


@register.filter
def indent_dict(value, indent_nb_space=4):
    indent = ' ' * indent_nb_space
    indent_nb = 0
    result = ''
    cr = False
    inc = 0
    for v in value:
        inc = inc + 1
        ind = indent * indent_nb
        if v == '{':
            cr = True
            indent_nb = indent_nb + 1
            if value[inc] == '}':
                result += v
                prev_v = v
                continue
            result += '%s\n' % v
        elif v == '}':
            indent_nb = indent_nb - 1
            ind = indent * indent_nb
            if prev_v == '{':
                result += v
                prev_v = v
                continue
            result += '\n%s%s' % (ind, v)
        elif v == ',':
            result += '%s\n' % v
            cr = True
        elif cr:
            if v == ' ':
                continue
            result += ind + v
            cr = False
        else:
            result += v
        prev_v = v

    return result
