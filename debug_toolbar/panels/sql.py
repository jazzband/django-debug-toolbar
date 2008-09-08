from debug_toolbar.panels import DebugPanel
from django.db import connection
from django.template.loader import render_to_string

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    name = 'SQL'
    
    def title(self):
        return '%d SQL Queries' % (len(connection.queries))

    def url(self):
        return ''

    def content(self):
        context = {'queries': connection.queries}
        return render_to_string('debug_toolbar/panels/sql.html', context)
