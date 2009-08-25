try:
    import resource
except ImportError:
    pass # Will fail on Win32 systems
import time
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel

class TimerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Timer'
    try: # if resource module not available, don't show content panel
        resource
    except NameError:
        has_content = False
        has_resource = False
    else:
        has_content = True
        has_resource = True

    def process_request(self, request):
        self._start_time = time.time()
        if self.has_resource:
            self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def process_response(self, request, response):
        self.total_time = (time.time() - self._start_time) * 1000
        if self.has_resource:
            self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)

    def nav_title(self):
        return _('Time')

    def nav_subtitle(self):
        if self.has_resource:
            utime = self._end_rusage.ru_utime - self._start_rusage.ru_utime
            stime = self._end_rusage.ru_stime - self._start_rusage.ru_stime
            return 'CPU: %0.2fms (%0.2fms)' % ((utime + stime) * 1000.0, self.total_time)
        else:
            return 'TOTAL: %0.2fms' % (self.total_time)

    def title(self):
        return 'Resource Usage'

    def url(self):
        return ''

    def _elapsed_ru(self, name):
        return getattr(self._end_rusage, name) - getattr(self._start_rusage, name)

    def content(self):

        utime = 1000 * self._elapsed_ru('ru_utime')
        stime = 1000 * self._elapsed_ru('ru_stime')
        vcsw = self._elapsed_ru('ru_nvcsw')
        ivcsw = self._elapsed_ru('ru_nivcsw')
        minflt = self._elapsed_ru('ru_minflt')
        majflt = self._elapsed_ru('ru_majflt')

# these are documented as not meaningful under Linux.  If you're running BSD
# feel free to enable them, and add any others that I hadn't gotten to before
# I noticed that I was getting nothing but zeroes and that the docs agreed. :-(
#
#        blkin = self._elapsed_ru('ru_inblock')
#        blkout = self._elapsed_ru('ru_oublock')
#        swap = self._elapsed_ru('ru_nswap')
#        rss = self._end_rusage.ru_maxrss
#        srss = self._end_rusage.ru_ixrss
#        urss = self._end_rusage.ru_idrss
#        usrss = self._end_rusage.ru_isrss

        rows = (
            ('User CPU time', '%0.3f msec' % utime),
            ('System CPU time', '%0.3f msec' % stime),
            ('Total CPU time', '%0.3f msec' % (utime + stime)),
            ('Elapsed time', '%0.3f msec' % self.total_time),
            ('Context switches', '%d voluntary, %d involuntary' % (vcsw, ivcsw)),
#            ('Memory use', '%d max RSS, %d shared, %d unshared' % (rss, srss, urss + usrss)),
#            ('Page faults', '%d no i/o, %d requiring i/o' % (minflt, majflt)),
#            ('Disk operations', '%d in, %d out, %d swapout' % (blkin, blkout, swap)),
        )
        context = {
            'rows': rows,
        }
        return render_to_string('debug_toolbar/panels/timer.html', context)
