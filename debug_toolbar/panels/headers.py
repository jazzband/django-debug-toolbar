from django.template import Context, Template
from debug_toolbar.panels import DebugPanel

class HeaderDebugPanel(DebugPanel):
    """
    A panel to display HTTP headers.
    """
    name = 'Header'
    # List of headers we want to display
    header_filter = [
        'CONTENT_TYPE',
        'HTTP_ACCEPT',
        'HTTP_ACCEPT_CHARSET',
        'HTTP_ACCEPT_ENCODING',
        'HTTP_ACCEPT_LANGUAGE',
        'HTTP_CACHE_CONTROL',
        'HTTP_CONNECTION',
        'HTTP_HOST',
        'HTTP_KEEP_ALIVE',
        'HTTP_REFERER',
        'HTTP_USER_AGENT',
        'QUERY_STRING',
        'REMOTE_ADDR',
        'REMOTE_HOST',
        'REQUEST_METHOD',
        'SCRIPT_NAME',
        'SERVER_NAME',
        'SERVER_PORT',
        'SERVER_PROTOCOL',
        'SERVER_SOFTWARE',
    ]
    def title(self):
        return 'HTTP Headers'

    def url(self):
        return ''

    def content(self):
        t = Template('''
            <dl>
                {% for h in headers %}
                    <dt><strong>{{ h.key }}</strong></dt>
                    <dd>{{ h.value }}</dd>
                {% endfor %}
            </dl>
        ''')
        headers = []
        for k, v in self.request.META.iteritems():
            if k in self.header_filter:
                headers.append({'key': k, 'value': v})
        c = Context({'headers': headers})
        return t.render(c)
