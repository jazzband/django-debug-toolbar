"""
Debug Toolbar middleware
"""
import imp
import thread

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import smart_unicode
from django.utils.importlib import import_module

import debug_toolbar.urls
from debug_toolbar.toolbar.loader import DebugToolbar

_HTML_TYPES = ('text/html', 'application/xhtml+xml')

def replace_insensitive(string, target, replacement):
    """
    Similar to string.replace() but is case insensitive
    Code borrowed from: http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string

class DebugToolbarMiddleware(object):
    """
    Middleware to set up Debug Toolbar on incoming request and render toolbar
    on outgoing response.
    """
    debug_toolbars = {}

    @classmethod
    def get_current(cls):
        return cls.debug_toolbars.get(thread.get_ident())

    def __init__(self):
        self._urlconfs = {}

        # Set method to use to decide to show toolbar
        self.show_toolbar = self._show_toolbar # default

        # The tag to attach the toolbar to
        self.tag= u'</body>'

        if hasattr(settings, 'DEBUG_TOOLBAR_CONFIG'):
            show_toolbar_callback = settings.DEBUG_TOOLBAR_CONFIG.get(
                'SHOW_TOOLBAR_CALLBACK', None)
            if show_toolbar_callback:
                self.show_toolbar = show_toolbar_callback

            tag = settings.DEBUG_TOOLBAR_CONFIG.get('TAG', None)
            if tag:
                self.tag = u'</' + tag + u'>'

    def _show_toolbar(self, request):
        if getattr(settings, 'TEST', False):
            return False

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if x_forwarded_for:
            remote_addr = x_forwarded_for.split(',')[0].strip()
        else:
            remote_addr = request.META.get('REMOTE_ADDR', None)

        # if not internal ip, and not DEBUG
        return remote_addr in settings.INTERNAL_IPS and bool(settings.DEBUG)

    def process_request(self, request):
        __traceback_hide__ = True
        if self.show_toolbar(request):
            urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
            if isinstance(urlconf, basestring):
                urlconf = import_module(getattr(request, 'urlconf', settings.ROOT_URLCONF))

            if urlconf not in self._urlconfs:
                new_urlconf = imp.new_module('urlconf')
                new_urlconf.urlpatterns = debug_toolbar.urls.urlpatterns + \
                        urlconf.urlpatterns

                if hasattr(urlconf, 'handler404'):
                    new_urlconf.handler404 = urlconf.handler404
                if hasattr(urlconf, 'handler500'):
                    new_urlconf.handler500 = urlconf.handler500

                self._urlconfs[urlconf] = new_urlconf

            request.urlconf = self._urlconfs[urlconf]

            toolbar = DebugToolbar(request)
            for panel in toolbar.panels:
                panel.process_request(request)
            self.__class__.debug_toolbars[thread.get_ident()] = toolbar

    def process_view(self, request, view_func, view_args, view_kwargs):
        __traceback_hide__ = True
        toolbar = self.__class__.debug_toolbars.get(thread.get_ident())
        if not toolbar:
            return
        for panel in toolbar.panels:
            panel.process_view(request, view_func, view_args, view_kwargs)

    def process_response(self, request, response):
        __traceback_hide__ = True
        ident = thread.get_ident()
        toolbar = self.__class__.debug_toolbars.get(ident)
        if not toolbar:
            return response
        if isinstance(response, HttpResponseRedirect):
            if not toolbar.config['INTERCEPT_REDIRECTS']:
                return response
            redirect_to = response.get('Location', None)
            if redirect_to:
                cookies = response.cookies
                response = render_to_response(
                    'debug_toolbar/redirect.html',
                    {'redirect_to': redirect_to}
                )
                response.cookies = cookies
        if 'gzip' not in response.get('Content-Encoding', '') and \
           response.get('Content-Type', '').split(';')[0] in _HTML_TYPES:
            for panel in toolbar.panels:
                panel.process_response(request, response)
            response.content = replace_insensitive(
                smart_unicode(response.content),
                self.tag,
                smart_unicode(toolbar.render_toolbar() + self.tag))
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        del self.__class__.debug_toolbars[ident]
        return response
