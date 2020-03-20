import json
import logging
from collections import OrderedDict

from django.conf.urls import url
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from debug_toolbar import settings as dt_settings
from debug_toolbar.panels import Panel
from debug_toolbar.panels.history import views
from debug_toolbar.panels.history.forms import HistoryStoreForm

logger = logging.getLogger(__name__)

CLEANSED_SUBSTITUTE = "********************"


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
        ]

    @property
    def nav_subtitle(self):
        return self.get_stats().get("request_url", "")

    def generate_stats(self, request, response):
        cleansed = request.POST.copy()
        for k in cleansed:
            cleansed[k] = CLEANSED_SUBSTITUTE
        self.record_stats(
            {
                "request_url": request.get_full_path(),
                "request_method": request.method,
                "post": json.dumps(cleansed, sort_keys=True, indent=4),
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
                "truncate_length": dt_settings.get_config()[
                    "HISTORY_POST_TRUNCATE_LENGTH"
                ],
            },
        )
