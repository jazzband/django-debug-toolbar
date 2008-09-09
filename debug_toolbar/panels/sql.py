from time import time
from debug_toolbar.panels import DebugPanel
from django.db import connection
from django.db.backends import util
from django.template.loader import render_to_string

class DatabaseStatTracker(util.CursorDebugWrapper):
    """
    Replacement for CursorDebugWrapper which stores additional information
    in `connection.queries`.
    """
    def execute(self, sql, params=()):
        start = time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time()
            # We keep `sql` to maintain backwards compatibility
            self.db.queries.append({
                'sql': self.db.ops.last_executed_query(self.cursor, sql, params),
                'time': stop - start,
                'raw_sql': sql,
                'params': params,
            })
util.CursorDebugWrapper = DatabaseStatTracker

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    name = 'SQL'
    has_content = True
    
    def title(self):
        total_time = sum(map(lambda q: float(q['time']) * 1000, connection.queries))
        return '%d SQL Queries (%.2fms)' % (len(connection.queries), total_time)

    def url(self):
        return ''

    def content(self):
        context = {'queries': connection.queries}
        return render_to_string('debug_toolbar/panels/sql.html', context)
