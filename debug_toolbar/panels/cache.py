import time
import inspect
try: 
    from cStringIO import StringIO
except ImportError: 
    import StringIO
from django.core import cache
from django.core.cache.backends.base import BaseCache
from django.template.loader import render_to_string
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
        self.get_many = 0
        self.deletes = 0
        self.total_time = 0

    def _get_func_info(self):
        stack = inspect.stack()[2]
        return (stack[1], stack[2], stack[3], stack[4])

    def get(self, key, default=None):
        t = time.time()
        value = self.cache.get(key, default)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        if value is None:
            self.misses += 1
        else:
            self.hits += 1
        self.gets += 1
        self.calls.append((this_time, 'get', (key,), self._get_func_info()))
        return value

    def set(self, key, value, timeout=None):
        t = time.time()
        self.cache.set(key, value, timeout)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        self.sets += 1
        self.calls.append((this_time, 'set', (key, value, timeout), self._get_func_info()))

    def delete(self, key):
        t = time.time()
        self.instance.delete(key, value)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        self.deletes += 1
        self.calls.append((this_time, 'delete', (key,), self._get_func_info()))

    def get_many(self, keys):
        t = time.time()
        results = self.cache.get_many(keys)
        this_time = time.time() - t
        self.total_time += this_time * 1000
        self.get_many += 1
        for key, value in results.iteritems():
            if value is None:
                self.misses += 1
            else:
                self.hits += 1
        self.calls.append((this_time, 'get_many', (keys,), self._get_func_info()))

class CacheDebugPanel(DebugPanel):
    """
    Panel that displays the cache statistics.
    """
    name = 'Cache'
    has_content = True

    def __init__(self):
        # This is hackish but to prevent threading issues is somewhat needed
        if isinstance(cache.cache, CacheStatTracker):
            cache.cache.reset()
            self.cache = cache.cache
        else:
            self.cache = CacheStatTracker(cache.cache)
            cache.cache = self.cache

    def title(self):
        return 'Cache: %.2fms' % self.cache.total_time

    def url(self):
        return ''

    def content(self):
        context = dict(
            cache_calls = len(self.cache.calls),
            cache_time = self.cache.total_time,
            cache = self.cache,
        )
        return render_to_string('debug_toolbar/panels/cache.html', context)