"""
Debug Toolbar middleware
"""
import re
from django.conf import settings
from django.utils.safestring import mark_safe
from debug_toolbar.toolbar.loader import DebugToolbar

_HTML_TYPES = ('text/html', 'application/xhtml+xml')
_END_HEAD_RE = re.compile(r'</head>', re.IGNORECASE)
_END_BODY_RE = re.compile(r'</body>', re.IGNORECASE)

class DebugToolbarMiddleware(object):
    """
    Middleware to set up Debug Toolbar on incoming request and render toolbar
    on outgoing response.
    """
    def __init__(self):
        self.debug_toolbar = None

    def process_request(self, request):
        if settings.DEBUG:
            self.debug_toolbar = DebugToolbar()
            self.debug_toolbar.load_panels()
        return None

    def process_response(self, request, response):
        if settings.DEBUG:
            if response['Content-Type'].split(';')[0] in _HTML_TYPES:
                #response.content = _END_HEAD_RE.sub(mark_safe(self.debug_toolbar.render_styles() + "%s" % match.group()), response.content)
                response.content = _END_BODY_RE.sub(mark_safe(self.debug_toolbar.render_toolbar() + '</body>'), response.content)
        return response
