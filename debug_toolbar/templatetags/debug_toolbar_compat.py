import django
from django.template import Library

if django.VERSION >= (1, 8):
    from django.template.defaulttags import cycle
else:
    from django.templatetags.future import cycle


register = Library()


cycle = register.tag(cycle)
