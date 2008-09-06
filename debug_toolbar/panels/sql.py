from debug_toolbar.panels import DebugPanel
from django.db import connection

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    def title(self):
        return '%d SQL Queries' % (len(connection.queries))

    def url(self):
        return ''

    def content(self):
        query_info = []
        for q in connection.queries:
            query_info.append('<dt><strong>%s</strong></dt><dd>%s</dd>' % (q['time'], q['sql']))
        return '<dl>%s</dl>' % (''.join(query_info))
