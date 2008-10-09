import time
from debug_toolbar.panels import DebugPanel
from django.conf import settings
from django.db import connection
from django.db.backends import util
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor

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
    sql = sql.replace('`,`', '`, `')
    sql = sql.replace('SELECT ', 'SELECT\n\t')
    sql = sql.replace('` FROM ', '`\nFROM\n\t')
    sql = sql.replace(' WHERE ', '\nWHERE\n\t')
    sql = sql.replace(' INNER JOIN ', '\nINNER JOIN\n\t')
    sql = sql.replace(' LEFT OUTER JOIN ', '\nLEFT OUTER JOIN\n\t')
    sql = sql.replace(' ORDER BY ', '\nORDER BY\n\t')
    # Use Pygments to highlight SQL if it's available
    try:
        from pygments import highlight
        from pygments.lexers import SqlLexer
        from pygments.formatters import HtmlFormatter
        sql = highlight(sql, SqlLexer(), HtmlFormatter())
    except ImportError:
        pass
    return sql
