import json
import logging
import re
import sys
from collections import OrderedDict

from django.conf import settings
from django.conf.urls import url
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel
from debug_toolbar.panels.history import views
from debug_toolbar.panels.history.forms import HistoryStoreForm

logger = logging.getLogger(__name__)

SENSITIVE_CREDENTIALS = re.compile("api|token|key|secret|password|signature", re.I)
CLEANSED_SUBSTITUTE = "********************"


def _clean_data(data):
    """
    Clean a dictionary of potentially sensitive info before
    sending to less secure functions.
    Not comprehensive

    Taken from django.contrib.auth.__init__.credentials
    """
    for key in data:
        if SENSITIVE_CREDENTIALS.search(key):
            data[key] = CLEANSED_SUBSTITUTE
    return data


class HistoryPanel(Panel):
    """ A panel to display History """

    title = _("History")
    nav_title = _("History")
    template = "debug_toolbar/panels/history.html"

    @property
    def is_historical(self):
        """The HistoryPanel should not be included in the historical panels."""
        return False

    @classmethod
    def get_urls(cls):
        return [
            url(r"^history_sidebar/$", views.history_sidebar, name="history_sidebar"),
            url(r"^history_refresh/$", views.history_refresh, name="history_refresh"),
        ]

    @property
    def nav_subtitle(self):
        return self.get_stats().get("request_url", "")

    def generate_stats(self, request, response):
        if request.method == "GET":
            data = request.GET.copy()
        else:
            data = request.POST.copy()
        # GraphQL tends to not be populated in POST. If the request seems
        # empty, check if it's a JSON request.
        if not data and request.META.get("CONTENT_TYPE") == "application/json":
            # Python <= 3.5's json.loads expects a string.
            data = json.loads(
                request.body
                if sys.version_info[:2] > (3, 5)
                else request.body.decode(request.encoding or settings.DEFAULT_CHARSET)
            )
        cleansed = _clean_data(data)
        self.record_stats(
            {
                "request_url": request.get_full_path(),
                "request_method": request.method,
                "data": cleansed,
                "time": timezone.now(),
            }
        )

    @property
    def content(self):
        """Content of the panel when it's displayed in full screen.

        Fetch every store for the toolbar and include it in the template.
        """
        stores = OrderedDict()
        for id, toolbar in reversed(self.toolbar._store.items()):
            stores[id] = {
                "toolbar": toolbar,
                "form": HistoryStoreForm(initial={"store_id": id}),
            }

        return render_to_string(
            self.template,
            {
                "current_store_id": self.toolbar.store_id,
                "stores": stores,
                "refresh_form": HistoryStoreForm(
                    initial={"store_id": self.toolbar.store_id}
                ),
            },
        )
