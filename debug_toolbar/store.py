from collections import OrderedDict

from django.utils.module_loading import import_string

from debug_toolbar import settings as dt_settings


class BaseStore:
    config = dt_settings.get_config().copy()

    @classmethod
    def get(cls, store_id):
        raise NotImplementedError

    @classmethod
    def all(cls):
        raise NotImplementedError

    @classmethod
    def set(cls, store_id, toolbar):
        raise NotImplementedError

    @classmethod
    def delete(cls, store_id):
        raise NotImplementedError


class MemoryStore(BaseStore):
    _store = OrderedDict()

    @classmethod
    def get(cls, store_id):
        return cls._store.get(store_id)

    @classmethod
    def all(cls):
        return cls._store.items()

    @classmethod
    def set(cls, store_id, toolbar):
        cls._store[store_id] = toolbar
        for _ in range(cls.config["RESULTS_CACHE_SIZE"], len(cls._store)):
            cls._store.popitem(last=False)

    @classmethod
    def delete(cls, store_id):
        del cls._store[store_id]


store = import_string(dt_settings.get_config()["TOOLBAR_STORE_CLASS"])
