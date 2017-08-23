Request Decorators
==================

This is a hypothetical function `increment` that'll store the cache value on `a.request`, where a is the only argument to the function:

Make necessary imports::

    >>> from plone.memoize.request import cache
    >>> from zope.annotation.interfaces import IAnnotations

::

    >>> def increment(a):
    ...     print('Someone or something called me')
    ...     return a + 1

Now we need to define this `a`.
For this, we'll inherit from `int` and add a `request` class variable.
Note that we also make our fake request `IAttributeAnnotatable`, because that's how the cache values are stored on the request::

    >>> from zope.publisher.browser import TestRequest
    >>> class A(int):
    ...     request = TestRequest()
    >>> from zope.interface import directlyProvides
    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> directlyProvides(A.request, IAttributeAnnotatable)

In addition to this request, we'll also need to set up a cache key generator.
We'll use the integer value of the only argument for that::

    >>> get_key = lambda fun, a, *args: a

Let's decorate our `increment` function now with the `cache` decorator.
We'll tell the decorator to use `args_hash` for generating the key.
`get_request` will tell the decorator how to actually find the `request` in the variable scope of the function itself::

    >>> cached_increment = \
    ...     cache(get_key=get_key, get_request='a.request')(increment)

    >>> cached_increment(A(1))
    Someone or something called me
    2
    >>> cached_increment(A(1))
    2
    >>> list(IAnnotations(A.request).items())
    [('None.increment:1', 2)]

If `request` is already part of the function's argument list, we don't need to specify any expression::

    >>> @cache(get_key=get_key)
    ... def increment_plus(a, request):
    ...     print('Someone or something called me')
    ...     return a + 1

    >>> increment_plus(42, A.request)
    Someone or something called me
    43
    >>> increment_plus(42, A.request)
    43
    >>> IAnnotations(A.request)['None.increment_plus:42']
    43

Create a function that can also take keyword arguments.
For the sake of convenience pass the request explicitly.
get_key must be modified to take kwargs into account::

    >>> def get_key(fun, a, request, **kwargs):
    ...     li = list(kwargs.items())
    ...     li.sort()
    ...     return "%s,%s" % (a, li)

    >>> @cache(get_key=get_key)
    ... def increment_kwargs(a, request, kwarg1=1, kwarg2=2):
    ...     print('Someone or something called me')
    ...     return a + 1

    >>> increment_kwargs(42, A.request, kwarg1='kwarg1', kwarg2='kwarg2')
    Someone or something called me
    43
    >>> increment_kwargs(42, A.request, kwarg1='kwarg1', kwarg2='kwarg2')
    43
    >>> IAnnotations(A.request)["None.increment_kwargs:42,[('kwarg1', 'kwarg1'), ('kwarg2', 'kwarg2')]"]
    43

Call increment_kwargs without specifying any keyword arguments::

    >>> increment_kwargs(42, A.request)
    Someone or something called me
    43
    >>> increment_kwargs(42, A.request)
    43
    >>> IAnnotations(A.request)["None.increment_kwargs:42,[]"]
    43

Call increment_kwargs and specify only the second keyword argument::

    >>> increment_kwargs(42, A.request, kwarg2='kwarg2')
    Someone or something called me
    43
    >>> increment_kwargs(42, A.request, kwarg2='kwarg2')
    43
    >>> IAnnotations(A.request)["None.increment_kwargs:42,[('kwarg2', 'kwarg2')]"]
    43

