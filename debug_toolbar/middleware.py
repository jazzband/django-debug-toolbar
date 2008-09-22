"""
Debug Toolbar middleware
"""
import re
from django.conf import settings
from django.utils.encoding import smart_str
from django.conf.urls.defaults import include, patterns
import debug_toolbar.urls
from debug_toolbar.toolbar.loader import DebugToolbar

_HTML_TYPES = ('text/html', 'application/xhtml+xml')
_END_HEAD_RE = re.compile(r'</head>', re.IGNORECASE)
_START_BODY_RE = re.compile(r'<body([^<]*)>', re.IGNORECASE)
_END_BODY_RE = re.compile(r'</body>', re.IGNORECASE)

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
        for panel in self.debug_toolbar.panels:
            panel.process_view(request, view_func, view_args, view_kwargs)

    def process_response(self, request, response):
        if response.status_code != 200:
            return response
        for panel in self.debug_toolbar.panels:
            panel.process_response(request, response)
        if self.show_toolbar(request):
            if response['Content-Type'].split(';')[0] in _HTML_TYPES:
                # Saving this here in case we ever need to inject into <head>
                #response.content = _END_HEAD_RE.sub(smart_str(self.debug_toolbar.render_styles() + "%s" % match.group()), response.content)
                response.content = _START_BODY_RE.sub(smart_str('<body\\1>' + self.debug_toolbar.render_toolbar()), response.content)
                response.content = _END_BODY_RE.sub(smart_str('<script src="' + request.META.get('SCRIPT_NAME', '') + '/__debug__/m/toolbar.js" type="text/javascript" charset="utf-8"></script></body>'), response.content)
        return response
