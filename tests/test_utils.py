import unittest

from django.test import override_settings

import debug_toolbar.utils
from debug_toolbar.utils import (
    get_name_from_obj,
    get_stack,
    get_stack_trace,
    render_stacktrace,
    tidy_stacktrace,
)


class GetNameFromObjTestCase(unittest.TestCase):
    def test_func(self):
        def x():
            return 1

        res = get_name_from_obj(x)
        self.assertEqual(res, "tests.test_utils.x")

    def test_lambda(self):
        res = get_name_from_obj(lambda: 1)
        self.assertEqual(res, "tests.test_utils.<lambda>")

    def test_class(self):
        class A:
            pass

        res = get_name_from_obj(A)
        self.assertEqual(res, "tests.test_utils.A")


class RenderStacktraceTestCase(unittest.TestCase):
    def test_importlib_path_issue_1612(self):
        trace = [
            ("/server/app.py", 1, "foo", ["code line 1", "code line 2"], {"foo": "bar"})
        ]
        result = render_stacktrace(trace)
        self.assertIn('<span class="djdt-path">/server/</span>', result)
        self.assertIn('<span class="djdt-file">app.py</span> in', result)

        trace = [
            (
                "<frozen importlib._bootstrap>",
                1,
                "foo",
                ["code line 1", "code line 2"],
                {"foo": "bar"},
            )
        ]
        result = render_stacktrace(trace)
        self.assertIn('<span class="djdt-path"></span>', result)
        self.assertIn(
            '<span class="djdt-file">&lt;frozen importlib._bootstrap&gt;</span> in',
            result,
        )


class StackTraceTestCase(unittest.TestCase):
    @override_settings(DEBUG_TOOLBAR_CONFIG={"HIDE_IN_STACKTRACES": []})
    def test_get_stack_trace_skip(self):
        stack_trace = get_stack_trace(skip=-1)
        self.assertTrue(len(stack_trace) > 2)
        self.assertEqual(stack_trace[-1][0], debug_toolbar.utils.__file__)
        self.assertEqual(stack_trace[-1][2], "get_stack_trace")
        self.assertEqual(stack_trace[-2][0], __file__)
        self.assertEqual(stack_trace[-2][2], "test_get_stack_trace_skip")

        stack_trace = get_stack_trace()
        self.assertTrue(len(stack_trace) > 1)
        self.assertEqual(stack_trace[-1][0], __file__)
        self.assertEqual(stack_trace[-1][2], "test_get_stack_trace_skip")

    def test_deprecated_functions(self):
        with self.assertWarns(DeprecationWarning):
            stack = get_stack()
        self.assertEqual(stack[0][1], __file__)
        with self.assertWarns(DeprecationWarning):
            stack_trace = tidy_stacktrace(reversed(stack))
        self.assertEqual(stack_trace[-1][0], __file__)
