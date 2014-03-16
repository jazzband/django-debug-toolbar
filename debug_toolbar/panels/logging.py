from __future__ import absolute_import, unicode_literals

import datetime
import logging
try:
    import threading
except ImportError:
    threading = None
from django.conf import settings
from django.utils.translation import ungettext, ugettext_lazy as _
from debug_toolbar.panels import Panel
from debug_toolbar.utils import ThreadCollector

MESSAGE_IF_STRING_REPRESENTATION_INVALID = '[Could not get log message]'


class LogCollector(ThreadCollector):

    def collect(self, item, thread=None):
        # Avoid logging SQL queries since they are already in the SQL panel
        # TODO: Make this check whether SQL panel is enabled
        if item.get('channel', '') == 'django.db.backends':
            return
        super(LogCollector, self).collect(item, thread)


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
        self.collector.collect(record)

collector = LogCollector()
collector_enabled = False


def enable_collector():
    """
    Enable the LogCollector if it has not already been enabled and DEBUG is True.
    """
    global collector_enabled

    if collector_enabled:
        return

    # Check to make sure DEBUG is enabled to prevent silent memory leaks.
    if settings.DEBUG:
        # We don't use enable/disable_instrumentation because logging is global.
        # We can't add thread-local logging handlers. Hopefully logging is cheap.
        logging_handler = ThreadTrackingHandler(collector)
        logging.root.setLevel(logging.NOTSET)
        logging.root.addHandler(logging_handler)
        collector_enabled = True


# Enable logging immediately if DEBUG is enabled
enable_collector()


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
        return ungettext("%(count)s message", "%(count)s messages",
                         record_count) % {'count': record_count}

    title = _("Log messages")

    def process_request(self, request):
        # The state of DEBUG can be changed after the app is first initialized; ensure
        # that the collector is in the right state.
        enable_collector()
        collector.clear_collection()

    def process_response(self, request, response):
        # The state of DEBUG can be changed after the app is first initialized; ensure
        # that the collector is in the right state.
        enable_collector()
        records = collector.get_collection()
        self._records[threading.currentThread()] = records
        collector.clear_collection()
        self.record_stats({'records': records})
