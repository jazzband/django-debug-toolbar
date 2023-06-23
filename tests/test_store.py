from django.test import TestCase
from django.test.utils import override_settings

from debug_toolbar import store


class SerializationTestCase(TestCase):
    def test_serialize(self):
        self.assertEqual(
            store.serialize({"hello": {"foo": "bar"}}),
            '{"hello": {"foo": "bar"}}',
        )

    def test_deserialize(self):
        self.assertEqual(
            store.deserialize('{"hello": {"foo": "bar"}}'),
            {"hello": {"foo": "bar"}},
        )


class BaseStoreTestCase(TestCase):
    def test_methods_are_not_implemented(self):
        # Find all the non-private and dunder class methods
        methods = [
            member for member in vars(store.BaseStore) if not member.startswith("_")
        ]
        self.assertEqual(len(methods), 7)
        with self.assertRaises(NotImplementedError):
            store.BaseStore.request_ids()
        with self.assertRaises(NotImplementedError):
            store.BaseStore.exists("")
        with self.assertRaises(NotImplementedError):
            store.BaseStore.set("")
        with self.assertRaises(NotImplementedError):
            store.BaseStore.clear()
        with self.assertRaises(NotImplementedError):
            store.BaseStore.delete("")
        with self.assertRaises(NotImplementedError):
            store.BaseStore.save_panel("", "", None)
        with self.assertRaises(NotImplementedError):
            store.BaseStore.panel("", "")


class MemoryStoreTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.store = store.MemoryStore

    def tearDown(self) -> None:
        self.store.clear()

    def test_ids(self):
        self.store.set("foo")
        self.store.set("bar")
        self.assertEqual(list(self.store.request_ids()), ["foo", "bar"])

    def test_exists(self):
        self.assertFalse(self.store.exists("missing"))
        self.store.set("exists")
        self.assertTrue(self.store.exists("exists"))

    def test_set(self):
        self.store.set("foo")
        self.assertEqual(list(self.store.request_ids()), ["foo"])

    def test_set_max_size(self):
        existing = self.store._config["RESULTS_CACHE_SIZE"]
        self.store._config["RESULTS_CACHE_SIZE"] = 1
        self.store.save_panel("foo", "foo.panel", "foo.value")
        self.store.save_panel("bar", "bar.panel", {"a": 1})
        self.assertEqual(list(self.store.request_ids()), ["bar"])
        self.assertEqual(self.store.panel("foo", "foo.panel"), {})
        self.assertEqual(self.store.panel("bar", "bar.panel"), {"a": 1})
        # Restore the existing config setting since this config is shared.
        self.store._config["RESULTS_CACHE_SIZE"] = existing

    def test_clear(self):
        self.store.save_panel("bar", "bar.panel", {"a": 1})
        self.store.clear()
        self.assertEqual(list(self.store.request_ids()), [])
        self.assertEqual(self.store.panel("bar", "bar.panel"), {})

    def test_delete(self):
        self.store.save_panel("bar", "bar.panel", {"a": 1})
        self.store.delete("bar")
        self.assertEqual(list(self.store.request_ids()), [])
        self.assertEqual(self.store.panel("bar", "bar.panel"), {})
        # Make sure it doesn't error
        self.store.delete("bar")

    def test_save_panel(self):
        self.store.save_panel("bar", "bar.panel", {"a": 1})
        self.assertEqual(list(self.store.request_ids()), ["bar"])
        self.assertEqual(self.store.panel("bar", "bar.panel"), {"a": 1})

    def test_panel(self):
        self.assertEqual(self.store.panel("missing", "missing"), {})
        self.store.save_panel("bar", "bar.panel", {"a": 1})
        self.assertEqual(self.store.panel("bar", "bar.panel"), {"a": 1})


class StubStore(store.BaseStore):
    pass


class GetStoreTestCase(TestCase):
    def test_get_store(self):
        self.assertIs(store.get_store(), store.MemoryStore)

    @override_settings(
        DEBUG_TOOLBAR_CONFIG={"TOOLBAR_STORE_CLASS": "tests.test_store.StubStore"}
    )
    def test_get_store_with_setting(self):
        self.assertIs(store.get_store(), StubStore)
