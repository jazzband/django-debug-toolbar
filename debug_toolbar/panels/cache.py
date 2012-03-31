import time
import inspect
import sys

from django.core import cache
from django.core.cache.backends.base import BaseCache
from django.utils.translation import ugettext_lazy as _, ungettext
from debug_toolbar.panels import DebugPanel


class CacheStatTracker(BaseCache):
    """A small class used to track cache calls."""
    def __init__(self, cache):
        self.cache = cache
        self.reset()

    def reset(self):
        self.calls = []
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.gets = 0
        self.get_manys = 0
        self.deletes = 0
        self.total_time = 0

    def _get_func_info(self):
        frame = sys._getframe(3)
        info = inspect.getframeinfo(frame)
        return (info[0], info[1], info[2], info[3])

    def get(self, *args, **kwargs):
        t = time.time()
        value = self.cache.get(*args, **kwargs)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        if value is None:
            self.misses += 1
        else:
            self.hits += 1
        self.gets += 1
        self.calls.append((this_time, 'get', args, kwargs, self._get_func_info()))
        return value

    def set(self, *args, **kwargs):
        t = time.time()
        self.cache.set(*args, **kwargs)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        self.sets += 1
        self.calls.append((this_time, 'set', args, kwargs, self._get_func_info()))

    def delete(self, *args, **kwargs):
        t = time.time()
        self.cache.delete(*args, **kwargs)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        self.deletes += 1
        self.calls.append((this_time, 'delete', args, kwargs, self._get_func_info()))

    def get_many(self, *args, **kwargs):
        t = time.time()
        results = self.cache.get_many(*args, **kwargs)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        self.get_manys += 1
        for key, value in results.iteritems():
            if value is None:
                self.misses += 1
            else:
                self.hits += 1
        self.calls.append((this_time, 'get_many', args, kwargs, self._get_func_info()))
        return results

    def make_key(self, *args, **kwargs):
        return self.cache.make_key(*args, **kwargs)

    def add(self, *args, **kwargs):
        return self.cache.add(*args, **kwargs)

    def has_key(self, *args, **kwargs):
        return self.cache.has_key(*args, **kwargs)

    def incr(self, *args, **kwargs):
        return self.cache.incr(*args, **kwargs)

    def decr(self, *args, **kwargs):
        return self.cache.decr(*args, **kwargs)

    def __contains__(self, key):
        return self.cache.__contains__(key)

    def set_many(self, *args, **kwargs):
        self.cache.set_many(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        self.cache.delete_many(*args, **kwargs)

    def clear(self):
        self.cache.clear()

    def validate_key(self, *args, **kwargs):
        self.cache.validate_key(*args, **kwargs)

    def incr_version(self, *args, **kwargs):
        return self.cache.incr_version(*args, **kwargs)

    def decr_version(self, *args, **kwargs):
        return self.cache.decr_version(*args, **kwargs)


class CacheDebugPanel(DebugPanel):
    """
    Panel that displays the cache statistics.
    """
    name = 'Cache'
    template = 'debug_toolbar/panels/cache.html'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(CacheDebugPanel, self).__init__(*args, **kwargs)
        cache.cache.reset()

    def nav_title(self):
        return _('Cache: %.2fms') % cache.cache.total_time

    def nav_subtitle(self):
        cache_calls = len(cache.cache.calls)
        return ungettext('%(cache_calls)d call in %(time).2fms',
                         '%(cache_calls)d calls in %(time).2fms',
                         cache_calls) % {'cache_calls': cache_calls,
                                         'time': cache.cache.total_time}

    def title(self):
        return _('Cache Usage')

    def url(self):
        return ''

    def process_response(self, request, response):
        self.record_stats({
            'cache_calls': len(cache.cache.calls),
            'cache_time': cache.cache.total_time,
            'cache': cache.cache,
        })

cache.cache = CacheStatTracker(cache.cache)
