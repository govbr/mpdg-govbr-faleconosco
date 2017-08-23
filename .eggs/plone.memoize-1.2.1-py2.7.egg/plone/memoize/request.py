# -*- coding: utf-8 -*-
"""Memoize decorator for methods.

Stores values in an annotation of the request.
"""
from functools import wraps
from plone.memoize import volatile
from zope.annotation.interfaces import IAnnotations
import inspect

_marker = object()


class RequestMemo(object):

    key = 'plone.memoize_request'

    def __init__(self, arg=0):
        self.arg = arg

    def __call__(self, func):

        @wraps(func)
        def memogetter(*args, **kwargs):
            request = None
            if isinstance(self.arg, int):
                request = args[self.arg]
            else:
                request = kwargs[self.arg]

            annotations = IAnnotations(request)
            cache = annotations.get(self.key, _marker)

            if cache is _marker:
                cache = annotations[self.key] = dict()

            key = (func.__module__, func.__name__,
                   args, frozenset(list(kwargs.items())))
            value = cache.get(key, _marker)
            if value is _marker:
                value = cache[key] = func(*args, **kwargs)
            return value
        return memogetter


def store_in_annotation_of(expr):

    def _store_in_annotation(fun, *args, **kwargs):
        # Use expr to find out the name of the request variable
        vars = {}
        spec = inspect.getargspec(fun)
        num_args = len(args)
        expected_num_args = num_args

        # Explicitly check for the correct number of arguments and
        # raise the appropriate TypeError if needed. This is done
        # to avoid the real problem being masked by an IndexError
        # later in this method.
        if spec[3] is not None:
            expected_num_args = len(spec[0]) - len(spec[3])
        if num_args != expected_num_args:
            raise TypeError("%s() takes exactly %s arguments (%s given)"
                            % (fun.__name__, expected_num_args, num_args))

        for index, name in enumerate(spec[0]):
            if index < num_args:
                vars[name] = args[index]
            else:
                vars[name] = kwargs.get(name, spec[3][index - num_args])
        request = eval(expr, {}, vars)
        return IAnnotations(request)
    return _store_in_annotation


def cache(get_key, get_request='request'):

    return volatile.cache(get_key,
                          get_cache=store_in_annotation_of(get_request))

memoize_diy_request = RequestMemo

__all__ = (memoize_diy_request, store_in_annotation_of, cache)
