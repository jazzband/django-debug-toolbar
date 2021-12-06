import inspect
import sys
import time
from collections import OrderedDict

try:
    from django.utils.connection import ConnectionProxy
except ImportError:
    ConnectionProxy = None

import django
from django.conf import settings
from django.core import cache
from django.core.cache import (
    DEFAULT_CACHE_ALIAS,
    CacheHandler,
    cache as original_cache,
    caches as original_caches,
)
from django.core.cache.backends.base import BaseCache
from django.dispatch import Signal
from django.middleware import cache as middleware_cache
from django.utils.translation import gettext_lazy as _, ngettext

from debug_toolbar import settings as dt_settings
from debug_toolbar.panels import Panel
from debug_toolbar.utils import (
    get_stack,
    get_template_info,
    render_stacktrace,
    tidy_stacktrace,
)

cache_called = Signal()


def send_signal(method):
    def wrapped(self, *args, **kwargs):
        t = time.time()
        value = method(self, *args, **kwargs)
        t = time.time() - t

        if dt_settings.get_config()["ENABLE_STACKTRACES"]:
            stacktrace = tidy_stacktrace(reversed(get_stack()))
        else:
            stacktrace = []

        template_info = get_template_info()
        cache_called.send(
            sender=self.__class__,
            time_taken=t,
            name=method.__name__,
            return_value=value,
            args=args,
            kwargs=kwargs,
            trace=stacktrace,
            template_info=template_info,
            backend=self.cache,
        )
        return value

    return wrapped


class CacheStatTracker(BaseCache):
    """A small class used to track cache calls."""

    def __init__(self, cache):
        self.cache = cache

    def __repr__(self):
        return str("<CacheStatTracker for %s>") % repr(self.cache)

    def _get_func_info(self):
        frame = sys._getframe(3)
        info = inspect.getframeinfo(frame)
        return (info[0], info[1], info[2], info[3])

    def __contains__(self, key):
        return self.cache.__contains__(key)

    def __getattr__(self, name):
        return getattr(self.cache, name)

    @send_signal
    def add(self, *args, **kwargs):
        return self.cache.add(*args, **kwargs)

    @send_signal
    def get(self, *args, **kwargs):
        return self.cache.get(*args, **kwargs)

    @send_signal
    def set(self, *args, **kwargs):
        return self.cache.set(*args, **kwargs)

    @send_signal
    def touch(self, *args, **kwargs):
        return self.cache.touch(*args, **kwargs)

    @send_signal
    def delete(self, *args, **kwargs):
        return self.cache.delete(*args, **kwargs)

    @send_signal
    def clear(self, *args, **kwargs):
        return self.cache.clear(*args, **kwargs)

    @send_signal
    def has_key(self, *args, **kwargs):
        # Ignore flake8 rules for has_key since we need to support caches
        # that may be using has_key.
        return self.cache.has_key(*args, **kwargs)  # noqa: W601

    @send_signal
    def incr(self, *args, **kwargs):
        return self.cache.incr(*args, **kwargs)

    @send_signal
    def decr(self, *args, **kwargs):
        return self.cache.decr(*args, **kwargs)

    @send_signal
    def get_many(self, *args, **kwargs):
        return self.cache.get_many(*args, **kwargs)

    @send_signal
    def set_many(self, *args, **kwargs):
        self.cache.set_many(*args, **kwargs)

    @send_signal
    def delete_many(self, *args, **kwargs):
        self.cache.delete_many(*args, **kwargs)

    @send_signal
    def incr_version(self, *args, **kwargs):
        return self.cache.incr_version(*args, **kwargs)

    @send_signal
    def decr_version(self, *args, **kwargs):
        return self.cache.decr_version(*args, **kwargs)


if django.VERSION < (3, 2):

    class CacheHandlerPatch(CacheHandler):
        def __getitem__(self, alias):
            actual_cache = super().__getitem__(alias)
            return CacheStatTracker(actual_cache)

else:

    class CacheHandlerPatch(CacheHandler):
        def __init__(self, settings=None):
            self._djdt_wrap = True
            super().__init__(settings=settings)

        def create_connection(self, alias):
            actual_cache = super().create_connection(alias)
            if self._djdt_wrap:
                return CacheStatTracker(actual_cache)
            else:
                return actual_cache


middleware_cache.caches = CacheHandlerPatch()


class CachePanel(Panel):
    """
    Panel that displays the cache statistics.
    """

    template = "debug_toolbar/panels/cache.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_time = 0
        self.hits = 0
        self.misses = 0
        self.calls = []
        self.counts = OrderedDict(
            (
                ("add", 0),
                ("get", 0),
                ("set", 0),
                ("touch", 0),
                ("delete", 0),
                ("clear", 0),
                ("get_many", 0),
                ("set_many", 0),
                ("delete_many", 0),
                ("has_key", 0),
                ("incr", 0),
                ("decr", 0),
                ("incr_version", 0),
                ("decr_version", 0),
            )
        )
        cache_called.connect(self._store_call_info)

    def _store_call_info(
        self,
        sender,
        name=None,
        time_taken=0,
        return_value=None,
        args=None,
        kwargs=None,
        trace=None,
        template_info=None,
        backend=None,
        **kw,
    ):
        if name == "get":
            if return_value is None:
                self.misses += 1
            else:
                self.hits += 1
        elif name == "get_many":
            for key, value in return_value.items():
                if value is None:
                    self.misses += 1
                else:
                    self.hits += 1
        time_taken *= 1000

        self.total_time += time_taken
        self.counts[name] += 1
        self.calls.append(
            {
                "time": time_taken,
                "name": name,
                "args": args,
                "kwargs": kwargs,
                "trace": render_stacktrace(trace),
                "template_info": template_info,
                "backend": backend,
            }
        )

    # Implement the Panel API

    nav_title = _("Cache")

    @property
    def nav_subtitle(self):
        cache_calls = len(self.calls)
        return (
            ngettext(
                "%(cache_calls)d call in %(time).2fms",
                "%(cache_calls)d calls in %(time).2fms",
                cache_calls,
            )
            % {"cache_calls": cache_calls, "time": self.total_time}
        )

    @property
    def title(self):
        count = len(getattr(settings, "CACHES", ["default"]))
        return (
            ngettext(
                "Cache calls from %(count)d backend",
                "Cache calls from %(count)d backends",
                count,
            )
            % {"count": count}
        )

    def enable_instrumentation(self):
        if django.VERSION < (3, 2):
            if isinstance(middleware_cache.caches, CacheHandlerPatch):
                cache.caches = middleware_cache.caches
            else:
                cache.caches = CacheHandlerPatch()
        else:
            for alias in cache.caches:
                if not isinstance(cache.caches[alias], CacheStatTracker):
                    cache.caches[alias] = CacheStatTracker(cache.caches[alias])

            if not isinstance(middleware_cache.caches, CacheHandlerPatch):
                middleware_cache.caches = cache.caches

        # Wrap the patched cache inside Django's ConnectionProxy
        if ConnectionProxy:
            cache.cache = ConnectionProxy(cache.caches, DEFAULT_CACHE_ALIAS)

    def disable_instrumentation(self):
        if django.VERSION < (3, 2):
            cache.caches = original_caches
            cache.cache = original_cache
            # While it can be restored to the original, any views that were
            # wrapped with the cache_page decorator will continue to use a
            # monkey patched cache.
            middleware_cache.caches = original_caches
        else:
            for alias in cache.caches:
                if isinstance(cache.caches[alias], CacheStatTracker):
                    cache.caches[alias] = cache.caches[alias].cache
            if ConnectionProxy:
                cache.cache = ConnectionProxy(cache.caches, DEFAULT_CACHE_ALIAS)
            # While it can be restored to the original, any views that were
            # wrapped with the cache_page decorator will continue to use a
            # monkey patched cache.

    def generate_stats(self, request, response):
        self.record_stats(
            {
                "total_calls": len(self.calls),
                "calls": self.calls,
                "total_time": self.total_time,
                "hits": self.hits,
                "misses": self.misses,
                "counts": self.counts,
            }
        )

    def generate_server_timing(self, request, response):
        stats = self.get_stats()
        value = stats.get("total_time", 0)
        title = "Cache {} Calls".format(stats.get("total_calls", 0))
        self.record_server_timing("total_time", title, value)
