from django.test import override_settings

from debug_toolbar.panels import Panel

from ..base import IntegrationTestCase


class CustomPanel(Panel):
    def title(self):
        return "Title with special chars &\"'<>"


@override_settings(
    DEBUG=True, DEBUG_TOOLBAR_PANELS=["tests.panels.test_custom.CustomPanel"]
)
class CustomPanelTestCase(IntegrationTestCase):
    def test_escapes_panel_title(self):
        response = self.client.get("/regular/basic/")
        self.assertContains(
            response,
            """
            <li id="djdt-CustomPanel" class="djDebugPanelButton" role="checkbox">
            <input type="checkbox" checked title="Disable for next and successive requests" data-cookie="djdtCustomPanel" aria-label="Disable for next and successive requests">
            <a class="CustomPanel" href="#" title="Title with special chars &amp;&quot;&#39;&lt;&gt;" role="link">
            Title with special chars &amp;&quot;&#39;&lt;&gt;
            </a>
            </li>
            """,
            html=True,
        )
        self.assertContains(
            response,
            """
            <div id="CustomPanel" class="djdt-panelContent djdt-hidden" role="region" aria-labelledby="djdt-CustomPanel-title">
            <div class="djDebugPanelTitle">
            <button type="button" class="djDebugClose" aria-label="Close">×</button>
            <h3>Title with special chars &amp;&quot;&#39;&lt;&gt;</h3>
            </div>
            <div class="djDebugPanelContent">
            <div class="djdt-loader" role="alert" aria-busy="true"></div>
            <div class="djdt-scroll" aria-live="polite" aria-atomic="true"></div>
            </div>
            </div>
            """,
            html=True,
        )
