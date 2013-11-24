from __future__ import absolute_import, unicode_literals

import datetime
import logging
try:
    import threading
except ImportError:
    threading = None
from django.utils.translation import ungettext, ugettext_lazy as _
from debug_toolbar.panels import Panel

MESSAGE_IF_STRING_REPRESENTATION_INVALID = '[Could not get log message]'


class LogCollector(object):
    def __init__(self):
        if threading is None:
            raise NotImplementedError(
                "threading module is not available, "
                "the logging panel cannot be used without it")
        self.records = {}  # a dictionary that maps threads to log records

    def add_record(self, record, thread=None):
        # Avoid logging SQL queries since they are already in the SQL panel
        # TODO: Make this check whether SQL panel is enabled
        if record.get('channel', '') == 'django.db.backends':
            return

        self.get_records(thread).append(record)

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is provided,
        returns a list for the current thread.
        """
        if thread is None:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]


class ThreadTrackingHandler(logging.Handler):
    def __init__(self, collector):
        logging.Handler.__init__(self)
        self.collector = collector

    def emit(self, record):
        try:
            message = record.getMessage()
        except Exception:
            message = MESSAGE_IF_STRING_REPRESENTATION_INVALID

        record = {
            'message': message,
            'time': datetime.datetime.fromtimestamp(record.created),
            'level': record.levelname,
            'file': record.pathname,
            'line': record.lineno,
            'channel': record.name,
        }
        self.collector.add_record(record)


collector = LogCollector()
logging_handler = ThreadTrackingHandler(collector)
logging.root.setLevel(logging.NOTSET)
logging.root.addHandler(logging_handler)  # register with logging

# We don't use enable/disable_instrumentation because we can't make these
# functions thread-safe and (hopefully) logging isn't too expensive.

try:
    import logbook
    logbook_supported = True
except ImportError:
    # logbook support is optional, so fail silently
    logbook_supported = False

if logbook_supported:
    class LogbookThreadTrackingHandler(logbook.handlers.Handler):
        def __init__(self, collector):
            logbook.handlers.Handler.__init__(self, bubble=True)
            self.collector = collector

        def emit(self, record):
            record = {
                'message': record.message,
                'time': record.time,
                'level': record.level_name,
                'file': record.filename,
                'line': record.lineno,
                'channel': record.channel,
            }
            self.collector.add_record(record)

    logbook_handler = LogbookThreadTrackingHandler(collector)
    logbook_handler.push_application()  # register with logbook


class LoggingPanel(Panel):
    template = 'debug_toolbar/panels/logging.html'

    def __init__(self, *args, **kwargs):
        super(LoggingPanel, self).__init__(*args, **kwargs)
        self._records = {}

    nav_title = _("Logging")

    @property
    def nav_subtitle(self):
        records = self._records[threading.currentThread()]
        record_count = len(records)
        return ungettext('%(count)s message', '%(count)s messages',
                         record_count) % {'count': record_count}

    title = _('Log Messages')

    def process_request(self, request):
        collector.clear_records()

    def process_response(self, request, response):
        records = collector.get_records()
        self._records[threading.currentThread()] = records
        collector.clear_records()
        self.record_stats({'records': records})
