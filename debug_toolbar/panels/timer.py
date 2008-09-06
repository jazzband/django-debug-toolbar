import time
from debug_toolbar.panels import DebugPanel

class TimerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took.
    """
    def __init__(self):
        self._start_time = time.time()

    def title(self):
        return 'Time: %0.2fms' % ((time.time() - self._start_time) * 1000)

    def url(self):
        return ''

    def content(self):
        return ''
