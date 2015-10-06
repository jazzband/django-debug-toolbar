# coding: utf-8

from __future__ import absolute_import, unicode_literals

import unittest

from django.contrib.auth.models import User
from django.db import connection
from django.db.utils import DatabaseError
from django.shortcuts import render
from django.test.utils import override_settings

from ..base import BaseTestCase


class SQLPanelTestCase(BaseTestCase):

    def setUp(self):
        super(SQLPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('SQLPanel')
        self.panel.enable_instrumentation()

    def tearDown(self):
        self.panel.disable_instrumentation()
        super(SQLPanelTestCase, self).tearDown()

    def test_disabled(self):
        config = {
            'DISABLE_PANELS': set(['debug_toolbar.panels.sql.SQLPanel'])
        }
        self.assertTrue(self.panel.enabled)
        with self.settings(DEBUG_TOOLBAR_CONFIG=config):
            self.assertFalse(self.panel.enabled)

    def test_recording(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)
        query = self.panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]['stacktrace']) > 0)

    def test_non_ascii_query(self):
        self.assertEqual(len(self.panel._queries), 0)

        # non-ASCII text query
        list(User.objects.extra(where=["username = 'apéro'"]))
        self.assertEqual(len(self.panel._queries), 1)

        # non-ASCII text parameters
        list(User.objects.filter(username='thé'))
        self.assertEqual(len(self.panel._queries), 2)

        # non-ASCII bytes parameters
        list(User.objects.filter(username='café'.encode('utf-8')))
        self.assertEqual(len(self.panel._queries), 3)

        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)

        # ensure the panel renders correctly
        self.assertIn('café', self.panel.content)

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        list(User.objects.filter(username='café'.encode('utf-8')))
        self.panel.process_response(self.request, self.response)
        # ensure the panel does not have content yet.
        self.assertNotIn('café', self.panel.content)
        self.panel.generate_stats(self.request, self.response)
        # ensure the panel renders correctly.
        self.assertIn('café', self.panel.content)

    @unittest.skipUnless(connection.vendor == 'postgresql',
                         'Test valid only on PostgreSQL')
    def test_erroneous_query(self):
        """
        Test that an error in the query isn't swallowed by the middleware.
        """
        try:
            connection.cursor().execute("erroneous query")
        except DatabaseError as e:
            self.assertTrue('erroneous query' in str(e))

    def test_disable_stacktraces(self):
        self.assertEqual(len(self.panel._queries), 0)

        with self.settings(DEBUG_TOOLBAR_CONFIG={'ENABLE_STACKTRACES': False}):
            list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)
        query = self.panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is empty
        self.assertEqual([], query[1]['stacktrace'])

    @override_settings(DEBUG=True, TEMPLATE_DEBUG=True,
                       TEMPLATE_LOADERS=('tests.loaders.LoaderWithSQL',))
    def test_regression_infinite_recursion(self):
        """
        Test case for when the template loader runs a SQL query that causes
        an infinite recursion in the SQL panel.
        """
        self.assertEqual(len(self.panel._queries), 0)

        render(self.request, "basic.html", {})

        # Two queries are logged because the loader runs SQL every time a
        # template is loaded and basic.html extends base.html.
        self.assertEqual(len(self.panel._queries), 2)
        query = self.panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]['stacktrace']) > 0)
