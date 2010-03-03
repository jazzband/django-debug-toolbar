try:
    import resource
except ImportError:
    pass # Will fail on Win32 systems
import time
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel
from debug_toolbar.debug.timer import DebugTimer

class TimerDebugPanel(DebugPanel):
    """
    Panel that displays the time a response took in milliseconds.
    """
    name = 'Timer'

    def __init__(self, context={}):
        super(TimerDebugPanel, self).__init__(context)
        self.timer = DebugTimer()
        self.has_content = self.timer.has_resource

    def process_request(self, request):
        self.timer.start(request)

    def process_response(self, request, response):
        self.timer.stop(request, response)

    def nav_title(self):
        return _('Time')

    def nav_subtitle(self):
        # TODO l10n
        if self.timer.has_resource:
            utime = self.timer._end_rusage.ru_utime - self.timer._start_rusage.ru_utime
            stime = self.timer._end_rusage.ru_stime - self.timer._start_rusage.ru_stime
            return 'CPU: %0.2fms (%0.2fms)' % ((utime + stime) * 1000.0, self.timer.total_time)
        else:
            return 'TOTAL: %0.2fms' % (self.timer.total_time)

    def title(self):
        return _('Resource Usage')

    def url(self):
        return ''

    def content(self):

        utime = 1000 * self.timer.elapsed_ru('ru_utime')
        stime = 1000 * self.timer.elapsed_ru('ru_stime')
        vcsw = self.timer.elapsed_ru('ru_nvcsw')
        ivcsw = self.timer.elapsed_ru('ru_nivcsw')
        minflt = self.timer.elapsed_ru('ru_minflt')
        majflt = self.timer.elapsed_ru('ru_majflt')

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

        # TODO l10n on values
        rows = (
            (_('User CPU time'), '%0.3f msec' % utime),
            (_('System CPU time'), '%0.3f msec' % stime),
            (_('Total CPU time'), '%0.3f msec' % (utime + stime)),
            (_('Elapsed time'), '%0.3f msec' % self.timer.total_time),
            (_('Context switches'), '%d voluntary, %d involuntary' % (vcsw, ivcsw)),
#            ('Memory use', '%d max RSS, %d shared, %d unshared' % (rss, srss, urss + usrss)),
#            ('Page faults', '%d no i/o, %d requiring i/o' % (minflt, majflt)),
#            ('Disk operations', '%d in, %d out, %d swapout' % (blkin, blkout, swap)),
        )

        context = self.context.copy()
        context.update({
            'rows': rows,
        })

        return render_to_string('debug_toolbar/panels/timer.html', context)
