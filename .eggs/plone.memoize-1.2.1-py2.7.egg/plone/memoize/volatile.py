# -*- coding: utf-8 -*-
"""A flexible caching decorator.

This module provides a cache decorator `cache` that you can use to
cache results of your functions or methods.
"""

from functools import wraps
import time


class CleanupDict(dict):
    """A dict that automatically cleans up items that haven't been
    accessed in a given timespan on *set*.
    """
    cleanup_period = 60 * 60 * 24 * 3  # 3 days

    def __init__(self, cleanup_period=None):
        super(CleanupDict, self).__init__()
        self._last_access = {}
        if cleanup_period is not None:
            self.cleanup_period = cleanup_period

    def __getitem__(self, key):
        value = super(CleanupDict, self).__getitem__(key)
        self._last_access[key] = time.time()
        return value

    def __setitem__(self, key, value):
        super(CleanupDict, self).__setitem__(key, value)
        self._last_access[key] = time.time()
        self._cleanup()

    def _cleanup(self):
        now = time.time()
        okay = now - self.cleanup_period
        for key, timestamp in list(self._last_access.items()):
            if timestamp < okay:
                del self._last_access[key]
                super(CleanupDict, self).__delitem__(key)

ATTR = '_v_memoize_cache'
CONTAINER_FACTORY = CleanupDict
_marker = object()


class DontCache(Exception):
    pass


def store_on_self(method, obj, *args, **kwargs):
    return obj.__dict__.setdefault(ATTR, CONTAINER_FACTORY())


def store_on_context(method, obj, *args, **kwargs):
    return obj.context.__dict__.setdefault(ATTR, CONTAINER_FACTORY())


def cache(get_key, get_cache=store_on_self):

    def decorator(fun):

        @wraps(fun)
        def replacement(*args, **kwargs):
            try:
                key = get_key(fun, *args, **kwargs)
            except DontCache:
                return fun(*args, **kwargs)
            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            cache = get_cache(fun, *args, **kwargs)
            cached_value = cache.get(key, _marker)
            if cached_value is _marker:
                cached_value = cache[key] = fun(*args, **kwargs)
            return cached_value
        return replacement
    return decorator
