Forever Decorators
==================

Memo decorators for globals - memoized values survive for as long as the process lives.

Stores values in a module-level variable.

Pay attention that is module is not thread-safe, so use it with care.

These remember a value "forever", i.e. until the process is restarted.
They work on both global functions and class functions.::

    >>> from plone.memoize import forever

    >>> @forever.memoize
    ... def remember(arg1, arg2):
    ...     print("Calculating")
    ...     return arg1 + arg2

No matter how many times we call this function with a particular set of arguments, it will only perform its calculation once::

    >>> remember(1, 1)
    Calculating
    2
    >>> remember(1, 1)
    2
    >>> remember(1, 2)
    Calculating
    3
    >>> remember(1, 2)
    3

This also works for methods in classes::

    >>> class Test(object):
    ...
    ...     @forever.memoize
    ...     def remember(self, arg1, arg2):
    ...         print("Calculating")
    ...         return arg1 + arg2

    >>> t = Test()
    >>> t.remember(1, 1)
    Calculating
    2
    >>> t.remember(1, 1)
    2
    >>> t.remember(1, 2)
    Calculating
    3
    >>> t.remember(1, 2)
    3

