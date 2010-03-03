from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel
from debug_toolbar.debug.headers import DebugHeaders

class HeaderDebugPanel(DebugPanel):
    """
    A panel to display HTTP headers.
    """
    name = 'Header'
    has_content = True

    def __init__(self, context={}):
        super(HeaderDebugPanel, self).__init__(context)
        self.debug_headers = DebugHeaders()

    def nav_title(self):
        return _('HTTP Headers')

    def title(self):
        return _('HTTP Headers')

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context.update({
            'headers': self.headers
        })
        return render_to_string('debug_toolbar/panels/headers.html', context)

    def process_request(self, request):
        self.headers = self.debug_headers.available_headers(request)

