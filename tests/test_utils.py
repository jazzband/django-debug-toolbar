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
        self.assertEqual(
            res, "tests.test_utils.GetNameFromObjTestCase.test_func.<locals>.x"
        )

    def test_lambda(self):
        res = get_name_from_obj(lambda: 1)
        self.assertEqual(
            res, "tests.test_utils.GetNameFromObjTestCase.test_lambda.<locals>.<lambda>"
        )

    def test_class(self):
        class A:
            pass

        res = get_name_from_obj(A)
        self.assertEqual(
            res, "tests.test_utils.GetNameFromObjTestCase.test_class.<locals>.A"
        )


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

    @override_settings(DEBUG_TOOLBAR_CONFIG={"ENABLE_STACKTRACES_LOCALS": True})
    def test_locals(self):
        # This wrapper class is necessary to mask the repr() of the list
        # returned by get_stack_trace(); otherwise the 'test_locals_value_1'
        # string will also be present in rendered_stack_2.
        class HideRepr:
            def __init__(self, value):
                self.value = value

        x = "test_locals_value_1"
        stack_1_wrapper = HideRepr(get_stack_trace())

        x = x.replace("1", "2")
        stack_2_wrapper = HideRepr(get_stack_trace())

        rendered_stack_1 = render_stacktrace(stack_1_wrapper.value)
        self.assertIn("test_locals_value_1", rendered_stack_1)
        self.assertNotIn("test_locals_value_2", rendered_stack_1)

        rendered_stack_2 = render_stacktrace(stack_2_wrapper.value)
        self.assertNotIn("test_locals_value_1", rendered_stack_2)
        self.assertIn("test_locals_value_2", rendered_stack_2)
