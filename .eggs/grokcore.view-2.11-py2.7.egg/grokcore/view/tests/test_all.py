import doctest
import os
import re
import unittest
from pkg_resources import resource_listdir

from zope.testing import cleanup, renormalizing
import zope.component.eventtesting

import grokcore.view
from grokcore.view.templatereg import file_template_registry

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS


def getlines(self, filename, module_globals=None):
    # Patch patch for python 2.6 to prevent a UnicodeDecodeError.
    m = self._DocTestRunner__LINECACHE_FILENAME_RE.match(filename)
    if m and m.group('name') == self.test.name:
        example = self.test.examples[int(m.group('examplenum'))]
        source = example.source
        if isinstance(source, unicode):
            source = source.encode('ascii', 'backslashreplace')
        return source.splitlines(True)
    else:
        return self.save_linecache_getlines(filename, module_globals)


doctest.DocTestRunner._DocTestRunner__patched_linecache_getlines = getlines


def setUp(test):
    zope.component.eventtesting.setUp(test)
    file_template_registry.ignore_templates('.svn')


def cleanUp(test):
    cleanup.cleanUp()

checker = renormalizing.RENormalizing([
    # str(Exception) has changed from Python 2.4 to 2.5 (due to
    # Exception now being a new-style class).  This changes the way
    # exceptions appear in traceback printouts.
    (re.compile(
        r"ConfigurationExecutionError: <class '([\w.]+)'>:"),
        r'ConfigurationExecutionError: \1:'), ])


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue
        test = None
        if filename.endswith('.py'):
            dottedname = 'grokcore.view.tests.%s.%s' % (name, filename[:-3])
            test = doctest.DocTestSuite(
                dottedname,
                setUp=setUp,
                tearDown=cleanUp,
                checker=checker,
                optionflags=optionflags)
        elif filename.endswith('.txt'):
            test = doctest.DocFileSuite(
                os.path.join(name, filename),
                optionflags=optionflags,
                setUp=setUp,
                tearDown=cleanUp,
                globs={'grok': grokcore.view})
        if test is not None:
            suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in [
            'contentprovider',
            'directoryresource',
            'skin',
            'template',
            'view']:
        suite.addTest(suiteFromPackage(name))
    suite.addTest(doctest.DocFileSuite(
        '../templatereg.txt',
        optionflags=optionflags,
        setUp=setUp,
        tearDown=cleanUp,
        ))
    return suite
