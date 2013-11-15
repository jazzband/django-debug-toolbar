from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils.html import escape
from django.utils.translation import ugettext as _

from debug_toolbar.toolbar import DebugToolbar


def render_panel(request):
    """Render the contents of a panel"""
    toolbar = DebugToolbar.fetch(int(request.GET['storage_id']))
    if toolbar is None:
        content = _("Data for this panel isn't available anymore. "
                    "Please reload the page and retry.")
        content = "<p>%s</p>" % escape(content)
    else:
        panel_id = request.GET['panel_id']
        for panel in toolbar.panels:
            if panel.dom_id() == panel_id:
                content = panel.content()
                break
    return HttpResponse(content)
