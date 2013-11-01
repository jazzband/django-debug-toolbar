from __future__ import unicode_literals

import logging

from debug_toolbar.panels.logger import (
    LoggingPanel, MESSAGE_IF_STRING_REPRESENTATION_INVALID)

from ..base import BaseTestCase


class LoggingPanelTestCase(BaseTestCase):

    def test_happy_case(self):
        logger = logging.getLogger(__name__)
        logger.info('Nothing to see here, move along!')

        logging_panel = self.toolbar.get_panel(LoggingPanel)
        logging_panel.process_response(None, None)
        records = logging_panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('Nothing to see here, move along!',
                         records[0]['message'])

    def test_formatting(self):
        logger = logging.getLogger(__name__)
        logger.info('There are %d %s', 5, 'apples')

        logging_panel = self.toolbar.get_panel(LoggingPanel)
        logging_panel.process_response(None, None)
        records = logging_panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('There are 5 apples',
                         records[0]['message'])

    def test_failing_formatting(self):
        class BadClass(object):
            def __str__(self):
                raise Exception('Please not stringify me!')

        logger = logging.getLogger(__name__)

        # should not raise exception, but fail silently
        logger.debug('This class is misbehaving: %s', BadClass())

        logging_panel = self.toolbar.get_panel(LoggingPanel)
        logging_panel.process_response(None, None)
        records = logging_panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual(MESSAGE_IF_STRING_REPRESENTATION_INVALID,
                         records[0]['message'])
