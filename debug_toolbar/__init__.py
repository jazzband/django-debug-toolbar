from __future__ import absolute_import, unicode_literals

__all__ = ['VERSION']


try:
    import pkg_resources
    VERSION = pkg_resources.get_distribution('django-debug-toolbar').version
except Exception:
    VERSION = 'unknown'


# Code that discovers files or modules in INSTALLED_APPS imports this module.

# Reference URLpatterns with an iterator to avoid circular imports.

def urlpatterns():
    from debug_toolbar.toolbar import DebugToolbar
    for pattern in DebugToolbar.get_urls():
        yield pattern


urls = urlpatterns(), 'djdt', 'djdt'


default_app_config = 'debug_toolbar.apps.DebugToolbarConfig'
