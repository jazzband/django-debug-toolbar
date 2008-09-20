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
        return '%d SQL Queries (%.2fms)' % (len(connection.queries), self._sql_time)

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
    sql = sql.replace('` FROM `', '` \n  FROM `')
    sql = sql.replace('` WHERE ', '` \n  WHERE ')
    sql = sql.replace('` INNER JOIN ', '` \n  INNER JOIN ')
    sql = sql.replace('` OUTER JOIN ', '` \n  OUTER JOIN ')
    sql = sql.replace(' ORDER BY ', ' \n  ORDER BY ')
    return sql
