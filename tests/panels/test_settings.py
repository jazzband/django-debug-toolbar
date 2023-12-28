from django.test import override_settings

from ..base import IntegrationTestCase


@override_settings(DEBUG=True)
class SettingsIntegrationTestCase(IntegrationTestCase):
    def test_panel_title(self):
        response = self.client.get("/regular/basic/")
        # The settings module is None due to using Django's UserSettingsHolder
        # in tests.
        self.assertContains(
            response,
            """
            <li id="djdt-SettingsPanel" class="djDebugPanelButton" role="checkbox">
            <input type="checkbox" checked title="Disable for next and successive requests" data-cookie="djdtSettingsPanel" aria-label="Disable for next and successive requests">
            <a class="SettingsPanel" href="#" title="Settings from None" role="link">Settings</a>
            </li>
            """,
            html=True,
        )
        self.assertContains(
            response,
            """
            <div id="SettingsPanel" class="djdt-panelContent djdt-hidden" role="region" aria-labelledby="djdt-SettingsPanel-title">
            <div class="djDebugPanelTitle">
            <button type="button" class="djDebugClose" aria-label="Close">×</button>
            <h3>Settings from None</h3>
            </div>
            <div class="djDebugPanelContent">
            <div class="djdt-loader" role="alert" aria-busy="true"></div>
            <div class="djdt-scroll" aria-live="polite" aria-atomic="true"></div>
            </div>
            </div>
            """,
            html=True,
        )
