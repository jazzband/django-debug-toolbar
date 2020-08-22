import datetime
import logging

from django.utils.translation import gettext_lazy as _, ngettext as __

from debug_toolbar.panels import Panel
from debug_toolbar.utils import ThreadCollector

try:
    import threading
except ImportError:
    threading = None

MESSAGE_IF_STRING_REPRESENTATION_INVALID = "[Could not get log message]"


class LogCollector(ThreadCollector):
    def collect(self, item, thread=None):
        # Avoid logging SQL queries since they are already in the SQL panel
        # TODO: Make this check whether SQL panel is enabled
        if item.get("channel", "") == "django.db.backends":
            return
        super().collect(item, thread)


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
            "message": message,
            "time": datetime.datetime.fromtimestamp(record.created),
            "level": record.levelname,
            "file": record.pathname,
            "line": record.lineno,
            "channel": record.name,
        }
        self.collector.collect(record)


# We don't use enable/disable_instrumentation because logging is global.
# We can't add thread-local logging handlers. Hopefully logging is cheap.

collector = LogCollector()
logging_handler = ThreadTrackingHandler(collector)
logging.root.addHandler(logging_handler)


class LoggingPanel(Panel):
    template = "debug_toolbar/panels/logging.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._records = {}

    nav_title = _("Logging")

    @property
    def nav_subtitle(self):
        stats = self.get_stats()
        record_count = len(stats["records"]) if stats else None
        return __("%(count)s message", "%(count)s messages", record_count) % {
            "count": record_count
        }

    title = _("Log messages")

    def process_request(self, request):
        collector.clear_collection()
        return super().process_request(request)

    def generate_stats(self, request, response):
        records = collector.get_collection()
        self._records[threading.currentThread()] = records
        collector.clear_collection()
        self.record_stats({"records": records})
