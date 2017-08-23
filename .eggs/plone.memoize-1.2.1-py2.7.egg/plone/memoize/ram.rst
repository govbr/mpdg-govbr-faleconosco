RAM Decorators
==============

A cache decorator that uses RAMCache by default.

Make necessary imports::

    >>> from plone.memoize.interfaces import ICacheChooser
    >>> from plone.memoize.ram import cache
    >>> from plone.memoize.ram import choose_cache
    >>> from plone.memoize.ram import global_cache
    >>> from plone.memoize.ram import RAMCacheAdapter
    >>> from zope import component
    >>> from zope import interface
    >>> from zope.ramcache import ram

::

    >>> def cache_key(fun, first, second):
    ...     return (first, second)
    >>> @cache(cache_key)
    ... def pow(first, second):
    ...     print('Someone or something called me')
    ...     return first ** second

    >>> pow(3, 2)
    Someone or something called me
    9
    >>> pow(3, 2)
    9

Let's cache another function::

    >>> @cache(cache_key)
    ... def add(first, second):
    ...     print('Someone or something called me')
    ...     return first + second

    >>> add(3, 2)
    Someone or something called me
    5
    >>> add(3, 2)
    5

Now invalidate the cache for the `pow` function::

    >>> pow(3, 2)
    9
    >>> global_cache.invalidate('None.pow')
    >>> pow(3, 2)
    Someone or something called me
    9

Make sure that we only invalidated the cache for the `pow` function::

    >>> add(3, 2)
    5

    >>> global_cache.invalidateAll()

You can register an ICacheChooser utility to override the cache used based on the function that is cached.
To do this, we'll first unregister the already registered global `choose_cache` function::

    >>> sm = component.getGlobalSiteManager()
    >>> sm.unregisterUtility(choose_cache)
    True

This customized cache chooser will use the `my_cache` for the `pow` function, and use the `global_cache` for all other functions::

    >>> my_cache = ram.RAMCache()
    >>> def my_choose_cache(fun_name):
    ...     if fun_name.endswith('.pow'):
    ...         return RAMCacheAdapter(my_cache)
    ...     else:
    ...         return RAMCacheAdapter(global_cache)
    >>> interface.directlyProvides(my_choose_cache, ICacheChooser)
    >>> sm.registerUtility(my_choose_cache)

Both caches are empty at this point::

    >>> len(global_cache.getStatistics())
    0
    >>> len(my_cache.getStatistics())
    0

Let's fill them::

    >>> pow(3, 2)
    Someone or something called me
    9
    >>> pow(3, 2)
    9
    >>> len(global_cache.getStatistics())
    0
    >>> len(my_cache.getStatistics())
    1

::

    >>> add(3, 2)
    Someone or something called me
    5
    >>> add(3, 2)
    5
    >>> len(global_cache.getStatistics())
    1
    >>> len(my_cache.getStatistics())
    1

