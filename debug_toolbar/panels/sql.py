from debug_toolbar.panels import DebugPanel
from django.db import connection
from django.template import Context, Template

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    def title(self):
        return '%d SQL Queries' % (len(connection.queries))

    def url(self):
        return ''

    def content(self):
        t = Template('''
            <dl>
                {% for q in queries %}
                    <dt><strong>{{ q.time }}</strong></dt>
                    <dd>{{ q.sql }}</dd>
                {% endfor %}
            </dl>
        ''')
        c = Context({'queries': connection.queries})
        return t.render(c)
