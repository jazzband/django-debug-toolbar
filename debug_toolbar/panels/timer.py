import time
from debug_toolbar.panels import DebugPanel

class TimerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took.
    """
    def __init__(self):
        self._start_time = time.time()

    def title(self):
        return 'Timer'

    def url(self):
        return ''

    def content(self):
        return "%f sec" % (time.time() - self._start_time)
