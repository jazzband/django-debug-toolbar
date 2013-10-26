from __future__ import unicode_literals

import re
from django import template
from django.utils.numberformat import format

register = template.Library()


@register.filter
def dotted_number(number):
    number = float(number)
    return format(number, '.', 6)


@register.filter(is_safe=True)
def nbspindent(obj):
    return re.sub(r'(?<=<br />)(\s+)[^ ]', lambda m: re.sub(r'\s', '&nbsp;', m.group(0)), obj)
