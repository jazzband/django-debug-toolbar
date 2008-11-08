import time, resource
from debug_toolbar.panels import DebugPanel

class TimerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Timer'

    def process_request(self, request):
        self._start_time = time.time()
        self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def process_response(self, request, response):
        self.total_time = (time.time() - self._start_time) * 1000
        self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def title(self):
        utime = self._end_rusage.ru_utime - self._start_rusage.ru_utime
        stime = self._end_rusage.ru_stime - self._start_rusage.ru_stime
        return 'Time: %0.2fms, %0.2fms CPU' % (self.total_time, (utime + stime) * 1000.0)

    def url(self):
        return ''

    def content(self):
        return ''
