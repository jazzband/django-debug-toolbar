from debug_toolbar.panels import DebugPanel

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    def title(self):
        return 'SQL Queries'

    def url(self):
        return ''

    def content(self):
        from django.db import connection
        query_info = []
        for q in connection.queries:
            query_info.append('<dt>%s</dt><dd>%s</dd>' % (q['time'], q['sql']))
        return '<dl>%s</dl>' % (''.join(query_info))

