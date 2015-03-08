from collections import defaultdict
import json

from django.db import connections
from django.utils.translation import ugettext_lazy as _


from debug_toolbar.panels import Panel
from debug_toolbar.panels.sql.tracking import ThreadLocalState


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
        self._cursors = {}

        sqls = ((alias, query['vendor'], query['raw_sql'], query['params'])
                for alias, queries in self._databases.items()
                for query in queries)
        plans = (self.explain(alias, vendor, sql, params)
                 for alias, vendor, sql, params in sqls)
        evals = (self.evaluate(alias, vendor, sql, plan)
                 for alias, vendor, sql, plan in plans)
        warnings = ((alias, vendor, sql, warn)
                    for alias, vendor, sql, warn in evals if warn)

        self.record_stats({'warnings': list(warnings)})

        for alias, cursor in self._cursors.items():
            cursor.close()

    def record(self, alias, **kwargs):
        # 'sql.tracking.ThreadLocalState.Wrapper' would call this function.
        self._databases[alias].append(kwargs)

    def explain(self, alias, vendor, sql, params):
        if alias not in self._cursors:
            conn = connections[alias]
            factory = getattr(conn, '_djdt_sqlwarnings_cursor', conn.cursor)
            self._cursors[alias] = factory()

        cursor = self._cursors[alias]
        params = json.loads(params)

        if vendor == 'sqlite':
            cursor.execute('EXPLAIN QUERY PLAN %s' % sql, params)
        elif vendor == 'postgresql':
            cursor.execute('EXPLAIN ANALYZE %s' % sql, params)
        else:
            cursor.execute('EXPLAIN %s' % sql, params)

        # FIXME: Serialize execution plan
        plan = cursor.fetchall()

        return alias, vendor, sql, plan

    def evaluate(self, alias, vendor, sql, plan):
        warning = plan  # FIXME: generate warning based on SQL execution plan
        return alias, vendor, sql, warning
