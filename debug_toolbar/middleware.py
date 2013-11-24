"""
Debug Toolbar middleware
"""

from __future__ import absolute_import, unicode_literals

import threading

from django.conf import settings
from django.utils.encoding import force_text

from debug_toolbar.toolbar import DebugToolbar
from debug_toolbar import settings as dt_settings

_HTML_TYPES = ('text/html', 'application/xhtml+xml')
# Handles python threading module bug - http://bugs.python.org/issue14308
threading._DummyThread._Thread__stop = lambda x: 1


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """
    if request.META.get('REMOTE_ADDR', None) not in settings.INTERNAL_IPS:
        return False

    if request.is_ajax():
        return False

    return bool(settings.DEBUG)


class DebugToolbarMiddleware(object):
    """
    Middleware to set up Debug Toolbar on incoming request and render toolbar
    on outgoing response.
    """
    debug_toolbars = {}

    def process_request(self, request):
        if not dt_settings.CONFIG['SHOW_TOOLBAR_CALLBACK'](request):
            return
        response = None
        toolbar = DebugToolbar(request)
        for panel in toolbar.enabled_panels:
            panel.enable_instrumentation()
        for panel in toolbar.enabled_panels:
            response = panel.process_request(request)
            if response:
                break
        self.__class__.debug_toolbars[threading.current_thread().ident] = toolbar
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        toolbar = self.__class__.debug_toolbars.get(threading.current_thread().ident)
        if not toolbar:
            return
        response = None
        for panel in toolbar.enabled_panels:
            response = panel.process_view(request, view_func, view_args, view_kwargs)
            if response:
                break
        return response

    def process_response(self, request, response):
        toolbar = self.__class__.debug_toolbars.pop(threading.current_thread().ident, None)
        if not toolbar or getattr(response, 'streaming', False):
            return response
        for panel in reversed(toolbar.enabled_panels):
            new_response = panel.process_response(request, response)
            if new_response:
                response = new_response
        for panel in reversed(toolbar.enabled_panels):
            panel.disable_instrumentation()
        if toolbar.config['SHOW_COLLAPSED'] and 'djdt' not in request.COOKIES:
            response.set_cookie('djdt', 'hide', 864000)
        if ('gzip' not in response.get('Content-Encoding', '') and
                response.get('Content-Type', '').split(';')[0] in _HTML_TYPES):
            content = force_text(response.content, encoding=settings.DEFAULT_CHARSET)
            try:
                insert_at = content.lower().rindex(dt_settings.CONFIG['INSERT_BEFORE'].lower())
            except ValueError:
                pass
            else:
                toolbar_content = toolbar.render_toolbar()
                response.content = content[:insert_at] + toolbar_content + content[insert_at:]
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        return response
