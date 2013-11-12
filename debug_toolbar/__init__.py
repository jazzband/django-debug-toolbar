from __future__ import unicode_literals


__all__ = ('VERSION',)


try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('django-debug-toolbar').version
except Exception as e:
    VERSION = 'unknown'


from .toolbar import DebugToolbar


urls = DebugToolbar.get_urls(), 'djdt', 'djdt'
