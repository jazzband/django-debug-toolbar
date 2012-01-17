import time
import uuid
import inspect
import datetime

from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel


class AjaxDebugPanel(DebugPanel):
    """
    Panel that displays recent AJAX requests.
    """
    name = 'Ajax'
    template = 'debug_toolbar/panels/ajax.html'
    has_content = True
    session_key = 'debug_toolbar_ajax_requests'

    def __init__(self, *args, **kwargs):
        super(AjaxDebugPanel, self).__init__(*args, **kwargs)
        self._num_requests = 0

    def nav_title(self):
        return _('Ajax')

    def nav_subtitle(self):
        # TODO l10n: use ngettext
        return "%d request%s" % (
            self._num_requests,
            (self._num_requests == 1) and '' or 's'
        )

    def title(self):
        return _('Ajax Requests')

    def url(self):
        return ''

    def storage(self, request):
        if self.session_key not in request.session:
            request.session[self.session_key] = []
        return request.session[self.session_key]

    def record(self, request, ddt_html):
        self.storage(request).append({
            'id': str(uuid.uuid4()),
            'time': datetime.datetime.now(),
            'path': request.path,
            'html': ddt_html,
        })

    def get_html(self, request, req_id):
        for ajax_request in self.storage(request):
            if ajax_request['id'] == req_id:
                return ajax_request['html']

    def get_context(self, request):
        return {
            'ajax_requests': self.storage(request),
        }

    def process_request(self, request):
        self._num_requests = len(self.storage(request))

    def process_response(self, request, response):
        self.record_stats(self.get_context(request))
