from django import template
from debug_toolbar import settings as dt_settings

register = template.Library()


@register.simple_tag
def js_custom_attribute():
    custom_attribute = dt_settings.get_config().get('JAVASCRIPT_CUSTOM_ATTRIBUTE')
    return ' ' + custom_attribute if custom_attribute else ''
