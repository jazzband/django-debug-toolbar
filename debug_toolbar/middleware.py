"""
Debug Toolbar middleware
"""
import thread

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import smart_unicode
from django.conf.urls.defaults import include, patterns

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
        self.override_url = True

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
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if x_forwarded_for:
            remote_addr = x_forwarded_for.split(',')[0].strip()
        else:
            remote_addr = request.META.get('REMOTE_ADDR', None)
        if not remote_addr in settings.INTERNAL_IPS \
            or (request.is_ajax() and \
                not debug_toolbar.urls._PREFIX in request.path) \
                    or not (settings.DEBUG or getattr(settings, 'TEST', False)):
            return False
        return True

    def process_request(self, request):
        if self.show_toolbar(request):
            if self.override_url:
                original_urlconf = __import__(getattr(request, 'urlconf', settings.ROOT_URLCONF), {}, {}, ['*'])
                debug_toolbar.urls.urlpatterns += patterns('',
                    ('', include(original_urlconf)),
                )
                if hasattr(original_urlconf, 'handler404'):
                    debug_toolbar.urls.handler404 = original_urlconf.handler404
                if hasattr(original_urlconf, 'handler500'):
                    debug_toolbar.urls.handler500 = original_urlconf.handler500
                self.override_url = False
            request.urlconf = 'debug_toolbar.urls'

            toolbar = DebugToolbar(request)
            for panel in toolbar.panels:
                panel.process_request(request)
            self.__class__.debug_toolbars[thread.get_ident()] = toolbar

    def process_view(self, request, view_func, view_args, view_kwargs):
        toolbar = self.__class__.debug_toolbars.get(thread.get_ident())
        if not toolbar:
            return
        for panel in toolbar.panels:
            panel.process_view(request, view_func, view_args, view_kwargs)

    def process_response(self, request, response):
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
