from __future__ import absolute_import, unicode_literals

import django

__all__ = ['VERSION']


try:
    import pkg_resources
    VERSION = pkg_resources.get_distribution('django-debug-toolbar').version
except Exception:
    VERSION = 'unknown'


# Code that discovers files or modules in INSTALLED_APPS imports this module.

if django.VERSION < (1, 9):
    urls = 'debug_toolbar.toolbar', 'djdt', 'djdt'
else:
    urls = 'debug_toolbar.toolbar', 'djdt'

default_app_config = 'debug_toolbar.apps.DebugToolbarConfig'
