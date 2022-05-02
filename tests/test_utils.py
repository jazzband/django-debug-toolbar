import unittest

from debug_toolbar.utils import get_name_from_obj, render_stacktrace


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
