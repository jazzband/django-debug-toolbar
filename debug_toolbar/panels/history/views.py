from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from debug_toolbar.decorators import require_show_toolbar
from debug_toolbar.panels.history.forms import HistoryStoreForm
from debug_toolbar.toolbar import DebugToolbar


@csrf_exempt
@require_show_toolbar
def history_sidebar(request):
    """Returns the selected debug toolbar history snapshot."""
    form = HistoryStoreForm(request.POST or None)

    if form.is_valid():
        store_id = form.cleaned_data["store_id"]
        toolbar = DebugToolbar.fetch(store_id)
        context = {}
        for panel in toolbar.panels:
            if not panel.is_historical:
                continue
            panel_context = {"panel": panel}
            context[panel.panel_id] = {
                "button": render_to_string(
                    "debug_toolbar/includes/panel_button.html", panel_context
                ),
                "content": render_to_string(
                    "debug_toolbar/includes/panel_content.html", panel_context
                ),
            }
        return JsonResponse(context)
    return HttpResponseBadRequest("Form errors")
