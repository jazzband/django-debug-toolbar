import time
from debug_toolbar.panels import DebugPanel

class TimerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Timer'

    def process_request(self, request):
        self._start_time = time.time()

    def process_response(self, request, response):
        self.total_time = (time.time() - self._start_time) * 1000

    def title(self):
        return 'Time: %0.2fms' % (self.total_time)

    def url(self):
        return ''

    def content(self):
        return ''
