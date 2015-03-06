from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import Panel


class SQLWarningsPanel(Panel):
    """
    Panel that warns certain patterns of the SQL queries run while processing
    the request.
    """

    nav_title = _('SQL Warnings')
    title = 'SQL Warnings'

    has_content = False

    def enable_instrumentation(self):
        pass

    def disable_instrumentation(self):
        pass
