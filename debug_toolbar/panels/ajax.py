import time
import uuid
import inspect
import datetime

from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel


class Storage:

    def __init__(self, request):
        self.session_key = None
        if hasattr(request, 'session'):
            self.session_key = request.session.session_key
            cache.add(self.session_key, [])
        
    def append(self, what):
        if self.session_key:
            toset = cache.get(self.session_key) or []
            toset.append(what)
            cache.set(self.session_key, toset)
        
    def __iter__(self):
        data = []
        if self.session_key:
            data = cache.get(self.session_key) or []
        for d in data:
            yield d

    def __len__(self):
        if self.session_key:
            return len(cache.get(self.session_key) or [])
        return 0
    
class AjaxDebugPanel(DebugPanel):
    """
    Panel that displays recent AJAX requests.
    """
    name = 'Ajax'
    template = 'debug_toolbar/panels/ajax.html'
    has_content = True

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
        return Storage(request)

    def record(self, request, ddt_html):
        self.storage(request).append({
            'id': str(uuid.uuid4()),
            'time': datetime.datetime.now(),
            'path': request.path,
            'html': ddt_html,
            'is_ajax': request.is_ajax()
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
