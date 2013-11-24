from __future__ import absolute_import, unicode_literals


__all__ = ['VERSION']


try:
    import pkg_resources
    VERSION = pkg_resources.get_distribution('django-debug-toolbar').version
except Exception:
    VERSION = 'unknown'


from .toolbar import DebugToolbar


urls = DebugToolbar.get_urls(), 'djdt', 'djdt'
