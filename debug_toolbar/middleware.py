"""
Debug Toolbar middleware
"""
import os

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
    def __init__(self):
        self.debug_toolbars = {}
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
                    or not settings.DEBUG:
            return False
        return True

    def process_request(self, request):
        if self.show_toolbar(request):
            if self.override_url:
                original_urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
                debug_toolbar.urls.urlpatterns += patterns('',
                    ('', include(original_urlconf)),
                )
                self.override_url = False
            request.urlconf = 'debug_toolbar.urls'

            self.debug_toolbars[request] = DebugToolbar(request)
            for panel in self.debug_toolbars[request].panels:
                panel.process_request(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request in self.debug_toolbars:
            for panel in self.debug_toolbars[request].panels:
                panel.process_view(request, view_func, view_args, view_kwargs)

    def process_response(self, request, response):
        if request not in self.debug_toolbars:
            return response
        if self.debug_toolbars[request].config['INTERCEPT_REDIRECTS']:
            if isinstance(response, HttpResponseRedirect):
                redirect_to = response.get('Location', None)
                if redirect_to:
                    response = render_to_response(
                        'debug_toolbar/redirect.html',
                        {'redirect_to': redirect_to}
                    )
        if response.status_code == 200:
            for panel in self.debug_toolbars[request].panels:
                panel.process_response(request, response)
            if response['Content-Type'].split(';')[0] in _HTML_TYPES:
                response.content = replace_insensitive(
                    smart_unicode(response.content), 
                    self.tag,
                    smart_unicode(self.debug_toolbars[request].render_toolbar() + self.tag))
            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)
        del self.debug_toolbars[request]
        return response
