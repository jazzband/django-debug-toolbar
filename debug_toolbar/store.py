import json
from collections import defaultdict, deque
from typing import Any, Dict, Iterable

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_str
from django.utils.module_loading import import_string

from debug_toolbar import settings as dt_settings


class DebugToolbarJSONEncoder(DjangoJSONEncoder):
    def default(self, o: Any) -> Any:
        try:
            return super().default(o)
        except TypeError:
            return force_str(o)


def serialize(data: Any) -> str:
    return json.dumps(data, cls=DebugToolbarJSONEncoder)


def deserialize(data: str) -> Any:
    return json.loads(data)


class BaseStore:
    _config = dt_settings.get_config().copy()

    @classmethod
    def ids(cls) -> Iterable:
        """The stored ids"""
        raise NotImplementedError

    @classmethod
    def exists(cls, request_id: str) -> bool:
        """Does the given request_id exist in the store"""
        raise NotImplementedError

    @classmethod
    def set(cls, request_id: str):
        """Set a request_id in the store"""
        raise NotImplementedError

    @classmethod
    def clear(cls):
        """Remove all requests from the request store"""
        raise NotImplementedError

    @classmethod
    def delete(cls, request_id: str):
        """Delete the store for the given request_id"""
        raise NotImplementedError

    @classmethod
    def save_panel(cls, request_id: str, panel_id: str, data: Any = None):
        """Save the panel data for the given request_id"""
        raise NotImplementedError

    @classmethod
    def panel(cls, request_id: str, panel_id: str) -> Any:
        """Fetch the panel data for the given request_id"""
        raise NotImplementedError


class MemoryStore(BaseStore):
    # ids is the collection of storage ids that have been used.
    # Use a dequeue to support O(1) appends and pops
    # from either direction.
    _ids: deque = deque()
    _request_store: Dict[str, Dict] = defaultdict(dict)

    @classmethod
    def ids(cls) -> Iterable:
        """The stored ids"""
        return cls._ids

    @classmethod
    def exists(cls, request_id: str) -> bool:
        """Does the given request_id exist in the request store"""
        return request_id in cls._ids

    @classmethod
    def set(cls, request_id: str):
        """Set a request_id in the request store"""
        if request_id not in cls._ids:
            cls._ids.append(request_id)
        for _ in range(len(cls._ids) - cls._config["RESULTS_CACHE_SIZE"]):
            removed_id = cls._ids.popleft()
            cls._request_store.pop(removed_id, None)

    @classmethod
    def clear(cls):
        """Remove all requests from the request store"""
        cls._ids.clear()
        cls._request_store.clear()

    @classmethod
    def delete(cls, request_id: str):
        """Delete the stored request for the given request_id"""
        cls._request_store.pop(request_id, None)
        try:
            cls._ids.remove(request_id)
        except ValueError:
            # The request_id doesn't exist in the collection of ids.
            pass

    @classmethod
    def save_panel(cls, request_id: str, panel_id: str, data: Any = None):
        """Save the panel data for the given request_id"""
        cls.set(request_id)
        cls._request_store[request_id][panel_id] = serialize(data)

    @classmethod
    def panel(cls, request_id: str, panel_id: str) -> Any:
        """Fetch the panel data for the given request_id"""
        try:
            data = cls._request_store[request_id][panel_id]
        except KeyError:
            return {}
        else:
            return deserialize(data)


def get_store():
    return import_string(dt_settings.get_config()["TOOLBAR_STORE_CLASS"])
