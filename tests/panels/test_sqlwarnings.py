from django.contrib.auth.models import User
from django.db import DEFAULT_DB_ALIAS

from ..base import BaseTestCase


class SQLWarningsPanelTestCase(BaseTestCase):
    def setUp(self):
        super(SQLWarningsPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('SQLWarningsPanel')
        self.panel.enable_instrumentation()

    def tearDown(self):
        self.panel.disable_instrumentation()
        super(SQLWarningsPanelTestCase, self).tearDown()

    def test_record(self):
        self.assertEqual(len(self.panel._databases[DEFAULT_DB_ALIAS]), 0)

        list(User.objects.all())

        self.assertEqual(len(self.panel._databases[DEFAULT_DB_ALIAS]), 1)
