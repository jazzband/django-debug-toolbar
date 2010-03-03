try:
    import resource
except ImportError:
    pass # Will fail on Win32 systems
import time


class DebugTimer(object):
    try: # if resource module not available, don't show content panel
        resource
    except NameError:
        has_resource = False
    else:
        has_resource = True

    def elapsed_ru(self, name):
        return getattr(self._end_rusage, name) - getattr(self._start_rusage, name)

    def start(self, request):
        self._start_time = time.time()
        if self.has_resource:
            self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def stop(self, request, response):
        self.total_time = (time.time() - self._start_time) * 1000
        if self.has_resource:
            self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)

