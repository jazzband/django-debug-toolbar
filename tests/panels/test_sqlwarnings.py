from django.contrib.auth.models import User
from django.db import DEFAULT_DB_ALIAS, connections

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

    def test_evaluate(self):
        # Mock vendor
        # FIXME: Use python-mock / unittest mock
        conn = connections[DEFAULT_DB_ALIAS]
        vendor = conn.vendor

        conn.vendor = 'unknown'
        plan = ((),)
        results = self.panel.evaluate(DEFAULT_DB_ALIAS, 'SQL', plan)
        alias, sql, warnings = results
        self.assertEqual(warnings, None)
        conn.vendor = vendor

        conn.vendor = 'mysql'
        plan = (('', '', '', '', '', '', '', '', '', ''),)
        results = self.panel.evaluate(DEFAULT_DB_ALIAS, 'SQL', plan)
        alias, sql, warnings = results
        self.assertEqual(warnings, None)
        conn.vendor = vendor

        conn.vendor = 'mysql'
        plan = (('', 'UNCACHEABLE SUBQUERY', '', '', '', '', '', '', '', ''),)
        results = self.panel.evaluate(DEFAULT_DB_ALIAS, 'SQL', plan)
        alias, sql, warnings = results
        self.assertEqual('Using uncacheable subquery' in warnings, True)
        conn.vendor = vendor

        conn.vendor = 'mysql'
        plan = (('', '', '', '', 'ALL', '', '', '', '', ''),)
        results = self.panel.evaluate(DEFAULT_DB_ALIAS, 'SQL', plan)
        alias, sql, warnings = results
        self.assertEqual('Using full table scan in table join' in warnings,
                         True)
        conn.vendor = vendor

        conn.vendor = 'mysql'
        plan = (('', '', '', '', '', '', '', '', '', 'USING FILESORT'),)
        results = self.panel.evaluate(DEFAULT_DB_ALIAS, 'SQL', plan)
        alias, sql, warnings = results
        self.assertEqual('Using filesort for sorting the result' in warnings,
                         True)
        conn.vendor = vendor
