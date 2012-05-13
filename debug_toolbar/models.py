from django.conf import settings
from django.utils.importlib import import_module

from debug_toolbar.toolbar.loader import load_panel_classes
from debug_toolbar.middleware import DebugToolbarMiddleware

loaded = False


def is_toolbar(cls):
    return (issubclass(cls, DebugToolbarMiddleware) or
            DebugToolbarMiddleware in getattr(cls, '__bases__', ()))


def iter_toolbar_middlewares():
    global loaded
    for middleware_path in settings.MIDDLEWARE_CLASSES:
        try:
            mod_path, cls_name = middleware_path.rsplit('.', 1)
            mod = import_module(mod_path)
            middleware_cls = getattr(mod, cls_name)
        except (AttributeError, ImportError, ValueError):
            continue
        if is_toolbar(middleware_cls) and not loaded:
            # we have a hit!
            loaded = True
            yield middleware_cls

for middleware_cls in iter_toolbar_middlewares():
    load_panel_classes()
