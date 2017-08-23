# -*- coding: utf-8 -*-
"""A cache decorator that uses RAMCache by default.
"""

from plone.memoize import volatile
from plone.memoize.interfaces import ICacheChooser
from zope import component
from zope import interface
from zope.ramcache import ram
from zope.ramcache.interfaces.ram import IRAMCache

import six

try:
    import pickle  # Python 3
except ImportError:
    import cPickle as pickle  # Python 2

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5


global_cache = ram.RAMCache()
global_cache.update(maxAge=86400)

DontCache = volatile.DontCache
MARKER = object()


class AbstractDict:

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class MemcacheAdapter(AbstractDict):

    def __init__(self, client, globalkey=''):
        self.client = client
        self.globalkey = globalkey and '%s:' % globalkey

    def _make_key(self, source):
        if issubclass(type(source), six.text_type):
            source = source.encode('utf-8')
        return md5(source).hexdigest()

    def __getitem__(self, key):
        cached_value = self.client.get(self.globalkey + self._make_key(key))
        if cached_value is None:
            raise KeyError(key)
        else:
            return pickle.loads(cached_value)

    def __setitem__(self, key, value):
        cached_value = pickle.dumps(value)
        self.client.set(self.globalkey + self._make_key(key), cached_value)


class RAMCacheAdapter(AbstractDict):

    def __init__(self, ramcache, globalkey=''):
        self.ramcache = ramcache
        self.globalkey = globalkey

    def _make_key(self, source):
        if issubclass(type(source), six.text_type):
            source = source.encode('utf-8')
        return md5(source).digest()

    def __getitem__(self, key):
        value = self.ramcache.query(self.globalkey,
                                    dict(key=self._make_key(key)),
                                    MARKER)
        if value is MARKER:
            raise KeyError(key)
        else:
            return value

    def __setitem__(self, key, value):
        self.ramcache.set(value,
                          self.globalkey,
                          dict(key=self._make_key(key)))


def choose_cache(fun_name):
    return RAMCacheAdapter(component.queryUtility(IRAMCache),
                           globalkey=fun_name)
interface.directlyProvides(choose_cache, ICacheChooser)


def store_in_cache(fun, *args, **kwargs):
    key = '%s.%s' % (fun.__module__, fun.__name__)
    cache_chooser = component.queryUtility(ICacheChooser)
    if cache_chooser is not None:
        return cache_chooser(key)
    else:
        return RAMCacheAdapter(global_cache, globalkey=key)


def cache(get_key):
    return volatile.cache(get_key, get_cache=store_in_cache)
