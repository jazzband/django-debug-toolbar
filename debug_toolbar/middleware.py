"""
Debug Toolbar middleware
"""
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
    index = no_case.find(target.lower())
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
        self.debug_toolbar = None

    def show_toolbar(self, request):
        if not settings.DEBUG:
            return False
        if request.is_ajax():
            return False
        if not request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return False
        return True

    def process_request(self, request):
        # Monkeypatch in the URLpatterns for the debug toolbar. The last item
        # in the URLpatterns needs to be ```('', include(ROOT_URLCONF))``` so
        # that the existing URLs load *after* the ones we patch in. However,
        # this is difficult to get right: a previous middleware might have
        # changed request.urlconf, so we need to pick that up instead.
        original_urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        debug_toolbar.urls.urlpatterns += patterns('',
            ('', include(original_urlconf)),
        )
        request.urlconf = 'debug_toolbar.urls'

        if self.show_toolbar(request):
            self.debug_toolbar = DebugToolbar(request)
            for panel in self.debug_toolbar.panels:
                panel.process_request(request)

        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        if self.debug_toolbar:
            for panel in self.debug_toolbar.panels:
                panel.process_view(request, view_func, view_args, view_kwargs)

    def process_response(self, request, response):
        if not self.debug_toolbar:
            return response
        if self.debug_toolbar.config['INTERCEPT_REDIRECTS']:
            if isinstance(response, HttpResponseRedirect):
                redirect_to = response.get('Location', None)
                if redirect_to:
                    response = render_to_response(
                        'debug_toolbar/redirect.html',
                        {'redirect_to': redirect_to}
                    )
        if response.status_code != 200:
            return response
        for panel in self.debug_toolbar.panels:
            panel.process_response(request, response)
        if response['Content-Type'].split(';')[0] in _HTML_TYPES:
            response.content = replace_insensitive(smart_unicode(response.content), u'</body>', smart_unicode(self.debug_toolbar.render_toolbar() + u'</body>'))
        return response
