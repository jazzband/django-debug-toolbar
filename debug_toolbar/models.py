from __future__ import unicode_literals

from django.conf import settings
from django.utils.importlib import import_module

from debug_toolbar.toolbar.loader import load_panel_classes
from debug_toolbar.middleware import DebugToolbarMiddleware


for middleware_path in settings.MIDDLEWARE_CLASSES:
    # Replace this with import_by_path in Django >= 1.6.
    try:
        mod_path, cls_name = middleware_path.rsplit('.', 1)
        mod = import_module(mod_path)
        middleware_cls = getattr(mod, cls_name)
    except (AttributeError, ImportError, ValueError):
        continue

    if issubclass(middleware_cls, DebugToolbarMiddleware):
        load_panel_classes()
        break
