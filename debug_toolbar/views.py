from django.http import JsonResponse
from django.utils.html import escape
from django.utils.translation import gettext as _

from debug_toolbar.decorators import require_show_toolbar
from debug_toolbar.store import get_store
from debug_toolbar.toolbar import stats_only_toolbar


@require_show_toolbar
def render_panel(request):
    """Render the contents of a panel"""
    store_id = request.GET["store_id"]
    if not get_store().exists(store_id):
        content = _(
            "Data for this panel isn't available anymore. "
            "Please reload the page and retry."
        )
        content = "<p>%s</p>" % escape(content)
        scripts = []
    else:
        toolbar = stats_only_toolbar(store_id)
        panel = toolbar.get_panel_by_id(request.GET["panel_id"])
        content = panel.content
        scripts = panel.scripts
    return JsonResponse({"content": content, "scripts": scripts})
