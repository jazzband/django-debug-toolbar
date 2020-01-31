import datetime
import json
from threading import local
from time import time

from django.utils.encoding import force_str

from debug_toolbar import settings as dt_settings
from debug_toolbar.utils import get_stack, get_template_info, tidy_stacktrace

try:
    from psycopg2._json import Json as PostgresJson
except ImportError:
    PostgresJson = None


class SQLQueryTriggered(Exception):
    """Thrown when template panel triggers a query"""

    pass


class ThreadLocalState(local):
    def __init__(self):
        self.enabled = True

    @property
    def Wrapper(self):
        if self.enabled:
            return NormalCursorWrapper
        return ExceptionCursorWrapper

    def recording(self, v):
        self.enabled = v


state = ThreadLocalState()
recording = state.recording  # export function


def wrap_cursor(connection, panel):
    if not hasattr(connection, "_djdt_cursor"):
        connection._djdt_cursor = connection.cursor
        connection._djdt_chunked_cursor = connection.chunked_cursor

        def cursor(*args, **kwargs):
            # Per the DB API cursor() does not accept any arguments. There's
            # some code in the wild which does not follow that convention,
            # so we pass on the arguments even though it's not clean.
            # See:
            # https://github.com/jazzband/django-debug-toolbar/pull/615
            # https://github.com/jazzband/django-debug-toolbar/pull/896
            return state.Wrapper(
                connection._djdt_cursor(*args, **kwargs), connection, panel
            )

        def chunked_cursor(*args, **kwargs):
            return state.Wrapper(
                connection._djdt_chunked_cursor(*args, **kwargs), connection, panel
            )

        connection.cursor = cursor
        connection.chunked_cursor = chunked_cursor
        return cursor


def unwrap_cursor(connection):
    if hasattr(connection, "_djdt_cursor"):
        del connection._djdt_cursor
        del connection.cursor
        del connection.chunked_cursor


class ExceptionCursorWrapper:
    """
    Wraps a cursor and raises an exception on any operation.
    Used in Templates panel.
    """

    def __init__(self, cursor, db, logger):
        pass

    def __getattr__(self, attr):
        raise SQLQueryTriggered()


class NormalCursorWrapper:
    """
    Wraps a cursor and logs queries.
    """

    def __init__(self, cursor, db, logger):
        self.cursor = cursor
        # Instance of a BaseDatabaseWrapper subclass
        self.db = db
        # logger must implement a ``record`` method
        self.logger = logger

    def _quote_expr(self, element):
        if isinstance(element, str):
            return "'%s'" % element.replace("'", "''")
        else:
            return repr(element)

    def _quote_params(self, params):
        if not params:
            return params
        if isinstance(params, dict):
            return {key: self._quote_expr(value) for key, value in params.items()}
        return [self._quote_expr(p) for p in params]

    def _decode(self, param):
        if PostgresJson and isinstance(param, PostgresJson):
            return param.dumps(param.adapted)
        # If a sequence type, decode each element separately
        if isinstance(param, (tuple, list)):
            return [self._decode(element) for element in param]

        # If a dictionary type, decode each value separately
        if isinstance(param, dict):
            return {key: self._decode(value) for key, value in param.items()}

        # make sure datetime, date and time are converted to string by force_str
        CONVERT_TYPES = (datetime.datetime, datetime.date, datetime.time)
        try:
            return force_str(param, strings_only=not isinstance(param, CONVERT_TYPES))
        except UnicodeDecodeError:
            return "(encoded string)"

    def _record(self, method, sql, params):
        start_time = time()
        try:
            return method(sql, params)
        finally:
            stop_time = time()
            duration = (stop_time - start_time) * 1000
            if dt_settings.get_config()["ENABLE_STACKTRACES"]:
                stacktrace = tidy_stacktrace(reversed(get_stack()))
            else:
                stacktrace = []
            _params = ""
            try:
                _params = json.dumps(self._decode(params))
            except TypeError:
                pass  # object not JSON serializable
            template_info = get_template_info()

            alias = getattr(self.db, "alias", "default")
            conn = self.db.connection
            vendor = getattr(conn, "vendor", "unknown")

            # Sql might be an object (such as psycopg Composed).
            # For logging purposes, make sure it's str.
            sql = str(sql)

            params = {
                "vendor": vendor,
                "alias": alias,
                "sql": self.db.ops.last_executed_query(
                    self.cursor, sql, self._quote_params(params)
                ),
                "duration": duration,
                "raw_sql": sql,
                "params": _params,
                "raw_params": params,
                "stacktrace": stacktrace,
                "start_time": start_time,
                "stop_time": stop_time,
                "is_slow": duration > dt_settings.get_config()["SQL_WARNING_THRESHOLD"],
                "is_select": sql.lower().strip().startswith("select"),
                "template_info": template_info,
            }

            if vendor == "postgresql":
                # If an erroneous query was ran on the connection, it might
                # be in a state where checking isolation_level raises an
                # exception.
                try:
                    iso_level = conn.isolation_level
                except conn.InternalError:
                    iso_level = "unknown"
                params.update(
                    {
                        "trans_id": self.logger.get_transaction_id(alias),
                        "trans_status": conn.get_transaction_status(),
                        "iso_level": iso_level,
                        "encoding": conn.encoding,
                    }
                )

            # We keep `sql` to maintain backwards compatibility
            self.logger.record(**params)

    def callproc(self, procname, params=None):
        return self._record(self.cursor.callproc, procname, params)

    def execute(self, sql, params=None):
        return self._record(self.cursor.execute, sql, params)

    def executemany(self, sql, param_list):
        return self._record(self.cursor.executemany, sql, param_list)

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
