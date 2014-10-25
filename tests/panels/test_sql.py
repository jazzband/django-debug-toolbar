# coding: utf-8

from __future__ import absolute_import, unicode_literals

import django
from django.contrib.auth.models import User
from django.db import connection
from django.db.utils import DatabaseError
from django.shortcuts import render
from django.utils import unittest
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

        # ensure the panel renders correctly
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

    @unittest.skipIf(django.VERSION < (1, 5),
                     "Django 1.4 loads the TEMPLATE_LOADERS before "
                     "override_settings can modify the settings.")
    @override_settings(DEBUG=True, TEMPLATE_DEBUG=True,
                       TEMPLATE_LOADERS=('tests.loaders.LoaderWithSQL',))
    def test_regression_infinite_recursion(self):
        """
        Test case for when the template loader runs a SQL query that causes
        an infinite recursion in the SQL panel.
        """
        self.assertEqual(len(self.panel._queries), 0)

        render(self.request, "basic.html", {})

        # ensure queries were logged
        # It's more than one because the SQL run in the loader is run every time
        # the template is rendered which is more than once.
        self.assertEqual(len(self.panel._queries), 3)
        query = self.panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]['stacktrace']) > 0)
