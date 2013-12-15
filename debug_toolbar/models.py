from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.core.urlresolvers import clear_url_caches, reverse, NoReverseMatch
from django.utils.importlib import import_module

import debug_toolbar
from debug_toolbar import settings as dt_settings
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


def is_toolbar_middleware_installed():
    return any(is_toolbar_middleware(middleware)
               for middleware in settings.MIDDLEWARE_CLASSES)


def prepend_to_setting(setting_name, value):
    """Insert value at the beginning of a list or tuple setting."""
    values = getattr(settings, setting_name)
    # Make a list [value] or tuple (value,)
    value = type(values)((value,))
    setattr(settings, setting_name, value + values)


def patch_internal_ips():
    if not settings.INTERNAL_IPS:
        prepend_to_setting('INTERNAL_IPS', '127.0.0.1')
        prepend_to_setting('INTERNAL_IPS', '::1')


def patch_middleware_classes():
    if not is_toolbar_middleware_installed():
        prepend_to_setting('MIDDLEWARE_CLASSES',
                           'debug_toolbar.middleware.DebugToolbarMiddleware')


def patch_root_urlconf():
    try:
        reverse('djdt:render_panel')
    except NoReverseMatch:
        urlconf_module = import_module(settings.ROOT_URLCONF)
        urlconf_module.urlpatterns = patterns('',                      # noqa
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ) + urlconf_module.urlpatterns
        clear_url_caches()


if dt_settings.PATCH_SETTINGS:
    patch_internal_ips()
    patch_middleware_classes()
    patch_root_urlconf()
