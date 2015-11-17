from __future__ import absolute_import, unicode_literals

import unittest

from debug_toolbar.utils import get_name_from_obj


class GetNameFromObjTestCase(unittest.TestCase):

    def test_func(self):
        def x():
            return 1
        res = get_name_from_obj(x)
        self.assertEqual(res, 'tests.test_utils.x')

    def test_lambda(self):
        res = get_name_from_obj(lambda: 1)
        self.assertEqual(res, 'tests.test_utils.<lambda>')

    def test_class(self):
        class A:
            pass
        res = get_name_from_obj(A)
        self.assertEqual(res, 'tests.test_utils.A')
