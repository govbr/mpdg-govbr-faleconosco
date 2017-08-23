# -*- coding: utf-8 -*-
from zope.component.testing import setUp
from zope.component.testing import tearDown
from zope.configuration.xmlconfig import XMLConfig
import doctest
import unittest

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS


def configurationSetUp(test):
    setUp()
    import zope.component
    XMLConfig('meta.zcml', zope.component)()
    import plone.memoize
    XMLConfig('configure.zcml', plone.memoize)()


def test_suite():
    tests = (
        doctest.DocFileSuite('README.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('compress.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('forever.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('instance.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('ram.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('request.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('view.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
        doctest.DocFileSuite('volatile.rst',
                             package="plone.memoize",
                             setUp=configurationSetUp,
                             tearDown=tearDown,
                             optionflags=optionflags),
    )

    return unittest.TestSuite(tests)
