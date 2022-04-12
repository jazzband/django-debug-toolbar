import datetime
import logging

from django.utils.translation import gettext_lazy as _, ngettext

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


# Preserve Python's fallback log mechanism before adding ThreadTrackingHandler.

# If the root logger has no handlers attached then everything that reaches it goes
# to the "handler of last resort".
# So a Django app that doesn't explicitly configure the root logger actually logs
# through logging.lastResort.
# However, logging.lastResort is not used after ThreadTrackingHandler gets added to
# the root logger below. This means that users who have LoggingPanel enabled might
# find their logs are gone from their app as soon as they install DDT.
# Explicitly adding logging.lastResort to logging.root's handler sidesteps this
# potential confusion.
# Note that if root has already been configured, or logging.lastResort has been
# removed, then the configuration is unchanged, so users who configured their
# logging aren't exposed to the opposite confusion of seeing extra log lines from
# their app.
if not logging.root.hasHandlers() and logging.lastResort is not None:
    logging.root.addHandler(logging.lastResort)

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
        return ngettext("%(count)s message", "%(count)s messages", record_count) % {
            "count": record_count
        }

    title = _("Log messages")

    def process_request(self, request):
        collector.clear_collection()
        return super().process_request(request)

    def generate_stats(self, request, response):
        records = collector.get_collection()
        self._records[threading.current_thread()] = records
        collector.clear_collection()
        self.record_stats({"records": records})
