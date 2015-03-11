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
        del conn._djdt_sqlwarnings_cursor


def mysql_warnings(plan):
    # Ref - https://dev.mysql.com/doc/refman/5.6/en/explain-output.html
    warnings = []

    for info in plan:
        select_type = info[1] or ''
        join_type = info[4] or ''
        extra = info[9] or ''

        if select_type.upper() == 'UNCACHEABLE SUBQUERY':
            warnings.append('Using uncacheable subquery')

        if join_type.upper() == 'ALL':
            warnings.append('Using full table scan in table join')

        if extra.upper() == 'USING FILESORT':
            warnings.append('Using filesort for sorting the result')

    if not warnings:
        return

    return frozenset(warnings)


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

        sqls = ((alias, query['raw_sql'], query['params'])
                for alias, queries in self._databases.items()
                for query in queries)
        plans = (self.explain(alias, sql, params)
                 for alias, sql, params in sqls)
        evals = (self.evaluate(alias, sql, plan)
                 for alias, sql, plan in plans if plan)
        warnings = ((alias, sql, warns)
                    for alias, sql, warns in evals if warns)

        self.record_stats({'warnings': list(warnings)})

        for alias, cursor in self._cursors.items():
            cursor.close()

    def record(self, alias, **kwargs):
        # 'sql.tracking.ThreadLocalState.Wrapper' would call this function.
        self._databases[alias].append(kwargs)

    def explain(self, alias, sql, params):
        if not sql.upper().startswith('SELECT '):
            return alias, sql, None

        if alias not in self._cursors:
            conn = connections[alias]
            factory = getattr(conn, '_djdt_sqlwarnings_cursor', conn.cursor)
            self._cursors[alias] = factory()

        vendor = connections[alias].vendor
        cursor = self._cursors[alias]
        params = json.loads(params)

        if vendor == 'sqlite':
            cursor.execute('EXPLAIN QUERY PLAN %s' % sql, params)
        elif vendor == 'postgresql':
            cursor.execute('EXPLAIN ANALYZE %s' % sql, params)
        else:
            cursor.execute('EXPLAIN %s' % sql, params)

        plan = cursor.fetchall()

        return alias, sql, plan

    def evaluate(self, alias, sql, plan):
        vendor = connections[alias].vendor

        # FIXME: Refactor this to support better extensibility
        if vendor == 'mysql':
            warnings = mysql_warnings(plan)
        else:
            warnings = None

        return alias, sql, warnings
