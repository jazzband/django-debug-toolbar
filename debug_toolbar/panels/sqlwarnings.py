from collections import defaultdict

from django.db import connections
from django.utils.translation import ugettext_lazy as _


from debug_toolbar.panels import Panel
from debug_toolbar.panels.sql.tracking import ThreadLocalState
from debug_toolbar.panels.sql.utils import reformat_sql


state = ThreadLocalState()


def wrap_cursor(conn, panel):
    if not hasattr(conn, '_djdt_sqlwarnings_cursor'):
        conn._djdt_sqlwarnings_cursor = conn.cursor

        def cursor():
            return state.Wrapper(conn._djdt_sqlwarnings_cursor(), conn, panel)

        conn.cursor = cursor
        return cursor


def unwrap_cursor(conn):
    if hasattr(conn, '_djdt_sqlwarnings_cursor'):
        del conn.cursor
        conn.cursor = conn._djdt_sqlwarnings_cursor


class SQLWarningsPanel(Panel):
    """
    Panel that warns certain patterns of the SQL queries run while processing
    the request.
    """

    nav_title = _('SQL Warnings')
    title = 'SQL Warnings'
    template = 'debug_toolbar/panels/sqlwarnings.html'

    def __init__(self, *args, **kwargs):
        super(SQLWarningsPanel, self).__init__(*args, **kwargs)

        self._databases = defaultdict(list)

    def enable_instrumentation(self):
        # This is thread-safe because database connections are thread-local.
        for conn in connections.all():
            wrap_cursor(conn, self)

    def disable_instrumentation(self):
        for conn in connections.all():
            unwrap_cursor(conn)

    def process_response(self, request, response):
        # FIXME: Call EXPLAIN and detect any non-scalable SQL execution plan.
        sqls = [(db, reformat_sql(query['sql']))
                for db, queries in self._databases.items()
                for query in queries]
        self.record_stats({'sqls': sqls})

    def record(self, alias, **kwargs):
        # 'sql.tracking.ThreadLocalState.Wrapper' would call this function.
        self._databases[alias].append(kwargs)
