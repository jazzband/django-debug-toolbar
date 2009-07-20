import os
import SocketServer
import time
import traceback
import django
from django.conf import settings
from django.db import connection
from django.db.backends import util
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from debug_toolbar.panels import DebugPanel

# Figure out some paths
django_path = os.path.realpath(os.path.dirname(django.__file__))
socketserver_path = os.path.realpath(os.path.dirname(SocketServer.__file__))

def tidy_stacktrace(strace):
    """
    Clean up stacktrace and remove all entries that:
    1. Are part of Django (except contrib apps)
    2. Are part of SocketServer (used by Django's dev server)
    3. Are the last entry (which is part of our stacktracing code)
    """
    trace = []
    for s in strace[:-1]:
        s_path = os.path.realpath(s[0])
        if django_path in s_path and not 'django/contrib' in s_path:
            continue
        if socketserver_path in s_path:
            continue
        trace.append((s[0], s[1], s[2], s[3]))
    return trace

class DatabaseStatTracker(util.CursorDebugWrapper):
    """
    Replacement for CursorDebugWrapper which stores additional information
    in `connection.queries`.
    """
    def execute(self, sql, params=()):
        start = time.time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time.time()
            stacktrace = tidy_stacktrace(traceback.extract_stack())
            _params = ''
            try:
                _params = simplejson.dumps([force_unicode(x) for x in params])
            except TypeError:
                pass # object not JSON serializable
            # We keep `sql` to maintain backwards compatibility
            self.db.queries.append({
                'sql': self.db.ops.last_executed_query(self.cursor, sql, params),
                'time': (stop - start) * 1000, # convert to ms
                'raw_sql': sql,
                'params': _params,
                'hash': sha_constructor(settings.SECRET_KEY + sql + _params).hexdigest(),
                'stacktrace': stacktrace,
            })
util.CursorDebugWrapper = DatabaseStatTracker

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing
    the request.
    """
    name = 'SQL'
    has_content = True

    def __init__(self):
        self._offset = len(connection.queries)
        self._sql_time = 0

    def title(self):
        self._sql_time = sum(map(lambda q: float(q['time']), connection.queries))
        num_queries = len(connection.queries) - self._offset
        return '%d SQL %s (%.2fms)' % (
            num_queries,
            (num_queries == 1) and 'query' or 'queries',
            self._sql_time
        )

    def url(self):
        return ''

    def content(self):
        sql_queries = connection.queries[self._offset:]
        for query in sql_queries:
            query['sql'] = reformat_sql(query['sql'])

        context = {
            'queries': sql_queries,
            'sql_time': self._sql_time,
            'is_mysql': settings.DATABASE_ENGINE == 'mysql',
        }
        return render_to_string('debug_toolbar/panels/sql.html', context)

def reformat_sql(sql):
    sql = sql.replace(',', ', ')
    sql = sql.replace('SELECT ', 'SELECT\n\t')
    sql = sql.replace(' FROM ', '\nFROM\n\t')
    sql = sql.replace(' WHERE ', '\nWHERE\n\t')
    sql = sql.replace(' INNER JOIN', '\n\tINNER JOIN')
    sql = sql.replace(' LEFT OUTER JOIN' , '\n\tLEFT OUTER JOIN')
    sql = sql.replace(' ORDER BY ', '\nORDER BY\n\t')
    sql = sql.replace(' HAVING ', '\nHAVING\n\t')
    sql = sql.replace(' GROUP BY ', '\nGROUP BY\n\t')
    # Use Pygments to highlight SQL if it's available
    try:
        from pygments import highlight
        from pygments.lexers import SqlLexer
        from pygments.formatters import HtmlFormatter
        sql = highlight(sql, SqlLexer(), HtmlFormatter())
    except ImportError:
        pass
    return sql
