from __future__ import unicode_literals

from django.conf import settings
from django.utils.importlib import import_module

from debug_toolbar.toolbar.loader import load_panel_classes
from debug_toolbar.middleware import DebugToolbarMiddleware


def is_toolbar_middleware(middleware_path):
    # Replace this with import_by_path in Django >= 1.6.
    try:
        mod_path, cls_name = middleware_path.rsplit('.', 1)
        mod = import_module(mod_path)
        middleware_cls = getattr(mod, cls_name)
    except (AttributeError, ImportError, ValueError):
        return
    return issubclass(middleware_cls, DebugToolbarMiddleware)


def prepend_to_setting(setting_name, value):
    """Insert value at the beginning of a list or tuple setting."""
    values = getattr(settings, setting_name)
    # Make a list [value] or tuple (value,)
    value = type(values)((value,))
    setattr(settings, setting_name, value + values)


if not settings.INTERNAL_IPS:
    prepend_to_setting('INTERNAL_IPS', '127.0.0.1')
    prepend_to_setting('INTERNAL_IPS', '::1')


if not any(is_toolbar_middleware(middleware)
           for middleware in settings.MIDDLEWARE_CLASSES):
    prepend_to_setting('MIDDLEWARE_CLASSES',
                       'debug_toolbar.middleware.DebugToolbarMiddleware')


load_panel_classes()
