# coding: utf-8

from __future__ import absolute_import, unicode_literals

import logging

from debug_toolbar.panels.logging import (
    MESSAGE_IF_STRING_REPRESENTATION_INVALID, collector,
)

from ..base import BaseTestCase


class LoggingPanelTestCase(BaseTestCase):

    def setUp(self):
        super(LoggingPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('LoggingPanel')
        self.logger = logging.getLogger(__name__)
        collector.clear_collection()

        # Assume the root logger has been configured with level=DEBUG.
        # Previously DDT forcefully set this itself to 0 (NOTSET).
        logging.root.setLevel(logging.DEBUG)

    def test_happy_case(self):
        self.logger.info('Nothing to see here, move along!')

        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)
        records = self.panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('Nothing to see here, move along!',
                         records[0]['message'])

    def test_formatting(self):
        self.logger.info('There are %d %s', 5, 'apples')

        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)
        records = self.panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('There are 5 apples',
                         records[0]['message'])

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        self.logger.info('café')
        self.panel.process_response(self.request, self.response)
        # ensure the panel does not have content yet.
        self.assertNotIn('café', self.panel.content)
        self.panel.generate_stats(self.request, self.response)
        # ensure the panel renders correctly.
        self.assertIn('café', self.panel.content)

    def test_failing_formatting(self):
        class BadClass(object):
            def __str__(self):
                raise Exception('Please not stringify me!')

        # should not raise exception, but fail silently
        self.logger.debug('This class is misbehaving: %s', BadClass())

        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)
        records = self.panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual(MESSAGE_IF_STRING_REPRESENTATION_INVALID,
                         records[0]['message'])
