import json
from collections import OrderedDict, defaultdict

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import import_string

from debug_toolbar import settings as dt_settings


class DebugToolbarJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            return str(o)


def serialize(data):
    return json.dumps(data, cls=DebugToolbarJSONEncoder)


def deserialize(data):
    return json.loads(data)


# Record stats in serialized fashion.
# Remove use of fetching the toolbar as a whole from the store.


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

    @classmethod
    def record_stats(cls, store_id, panel_id, stats):
        raise NotImplementedError


class MemoryStore(BaseStore):
    _store = OrderedDict()
    _stats = defaultdict(dict)

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

    @classmethod
    def save_panel(cls, store_id, panel_id, stats=None):
        cls._stats[store_id][panel_id] = serialize(stats)

    @classmethod
    def panel(cls, store_id, panel_id):
        try:
            data = cls._stats[store_id][panel_id]
        except KeyError:
            data = None
        return {} if data is None else deserialize(data)


store = import_string(dt_settings.get_config()["TOOLBAR_STORE_CLASS"])
