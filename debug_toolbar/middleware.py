"""
Debug Toolbar middleware
"""

from __future__ import unicode_literals

import threading

from django.conf import settings
from django.utils.encoding import force_text

from debug_toolbar.toolbar import DebugToolbar
from debug_toolbar.utils import settings as dt_settings

_HTML_TYPES = ('text/html', 'application/xhtml+xml')
# Handles python threading module bug - http://bugs.python.org/issue14308
threading._DummyThread._Thread__stop = lambda x: 1


def replace_insensitive(string, target, replacement):
    """
    Similar to string.replace() but is case insensitive.
    Code borrowed from:
    http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else:  # no results so return the original string
        return string


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

    def __init__(self):
        # The method to call to decide to show the toolbar
        self.show_toolbar = dt_settings.CONFIG['SHOW_TOOLBAR_CALLBACK'] or show_toolbar

        # The tag to attach the toolbar to
        self.tag = '</%s>' % dt_settings.CONFIG['TAG']

    def process_request(self, request):
        if not self.show_toolbar(request):
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
        if ('gzip' not in response.get('Content-Encoding', '') and
                response.get('Content-Type', '').split(';')[0] in _HTML_TYPES):
            response.content = replace_insensitive(
                force_text(response.content, encoding=settings.DEFAULT_CHARSET),
                self.tag,
                force_text(toolbar.render_toolbar() + self.tag))
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        return response
