import json
from collections import defaultdict

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
    def ids(cls):
        raise NotImplementedError

    @classmethod
    def exists(cls, store_id):
        raise NotImplementedError

    @classmethod
    def set(cls, store_id):
        raise NotImplementedError

    @classmethod
    def delete(cls, store_id):
        raise NotImplementedError


class MemoryStore(BaseStore):
    _ids = list()
    _stats = defaultdict(dict)

    @classmethod
    def ids(cls):
        return cls._ids

    @classmethod
    def exists(cls, store_id):
        return store_id in cls._ids

    @classmethod
    def set(cls, store_id):
        if store_id not in cls._ids:
            cls._ids.append(store_id)
        if len(cls._ids) > cls.config["RESULTS_CACHE_SIZE"]:
            cls.delete(cls._ids[0])

    @classmethod
    def delete(cls, store_id):
        if store_id in cls._stats:
            del cls._stats[store_id]
        if store_id in cls._ids:
            cls._ids.remove(store_id)

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
