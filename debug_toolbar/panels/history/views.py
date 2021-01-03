from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string

from debug_toolbar.decorators import require_show_toolbar, signed_data_view
from debug_toolbar.forms import SignedDataForm
from debug_toolbar.panels.history.forms import HistoryStoreForm
from debug_toolbar.store import store


@require_show_toolbar
@signed_data_view
def history_sidebar(request, verified_data):
    """Returns the selected debug toolbar history snapshot."""
    form = HistoryStoreForm(verified_data)

    if form.is_valid():
        store_id = form.cleaned_data["store_id"]
        toolbar = store.get(store_id)
        context = {}
        if toolbar is None:
            # When the store_id has been popped already due to
            # RESULTS_CACHE_SIZE
            return JsonResponse(context)
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


@require_show_toolbar
@signed_data_view
def history_refresh(request, verified_data):
    """Returns the refreshed list of table rows for the History Panel."""
    form = HistoryStoreForm(verified_data)

    if form.is_valid():
        requests = []
        for id, toolbar in list(reversed(store.all())):
            requests.append(
                {
                    "id": id,
                    "content": render_to_string(
                        "debug_toolbar/panels/history_tr.html",
                        {
                            "id": id,
                            "store_context": {
                                "toolbar": toolbar,
                                "form": SignedDataForm(
                                    initial=HistoryStoreForm(
                                        initial={"store_id": id}
                                    ).initial
                                ),
                            },
                        },
                    ),
                }
            )

        return JsonResponse({"requests": requests})
    return HttpResponseBadRequest("Form errors")
