import time
from debug_toolbar.panels import DebugPanel
from django.db import connection
from django.db.backends import util
from django.template.loader import render_to_string
from django.utils import simplejson

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
            # We keep `sql` to maintain backwards compatibility
            self.db.queries.append({
                'sql': self.db.ops.last_executed_query(self.cursor, sql, params),
                'time': stop - start,
                'raw_sql': sql,
                'params': simplejson.dumps(params),
            })
util.CursorDebugWrapper = DatabaseStatTracker

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    name = 'SQL'
    has_content = True
    
    def __init__(self, request):
        super(SQLDebugPanel, self).__init__(request)
        self._offset = len(connection.queries)
        self._sql_time = 0

    def title(self):
        self._sql_time = sum(map(lambda q: float(q['time']) * 1000, connection.queries))
        return '%d SQL %s (%.2fms)' % (
            len(connection.queries), 
            (len(connection.queries) == 1) and 'query' or 'queries',
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
        }
        return render_to_string('debug_toolbar/panels/sql.html', context)

def reformat_sql(sql):
    sql = sql.replace('`,`', '`, `')
    sql = sql.replace('SELECT ', 'SELECT\n\t')
    sql = sql.replace('` FROM ', '`\nFROM\n\t')
    sql = sql.replace('` WHERE ', '`\nWHERE\n\t')
    sql = sql.replace('` INNER JOIN ', '`\nINNER JOIN\n\t')
    sql = sql.replace('` OUTER JOIN ', '`\nOUTER JOIN\n\t')
    sql = sql.replace(' ORDER BY ', '\nORDER BY\n\t')
    # Use Pygments to highlight SQL if it's available
    try:
        from pygments import highlight
        from pygments.lexers import SqlLexer
        from pygments.formatters import HtmlFormatter
        sql = highlight(sql, SqlLexer(), HtmlFormatter(noclasses=True))
    except ImportError:
        pass
    return sql
