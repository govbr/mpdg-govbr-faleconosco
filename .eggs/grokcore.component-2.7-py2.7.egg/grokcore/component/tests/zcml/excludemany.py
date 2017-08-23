"""
It allows to exclude a many packages or modules from beeing grokked.

These packages or modules can be specified using unix shell-style wildcards

There is a NameError in `.excludemanypkg.file_1` which is raised when this
module is not excluded:

>>> xmlconfig.string('''
...     <configure xmlns:grok="http://namespaces.zope.org/grok">
...       <include package="grokcore.component" file="meta.zcml"/>
...       <grok:grok package="." />
...     </configure>''', context)
Traceback (most recent call last):
ZopeXMLConfigurationError: File "<string>", line 4.6-4.31
    NameError: name 'asdf' is not defined

There is a NameError in `.excludemanypkg.test_asdf`, too which is raised when
this module is not excluded:

>>> xmlconfig.string('''
...     <configure xmlns:grok="http://namespaces.zope.org/grok">
...       <include package="grokcore.component" file="meta.zcml"/>
...       <grok:grok package="."
...                  exclude="file_*" />
...     </configure>''', context)
Traceback (most recent call last):
ZopeXMLConfigurationError: File "<string>", line 4.6-5.36
    NameError: name 'qwe' is not defined


Excluding both 'file_1` and `test_asdf`allows to successfully grok the module:

>>> xmlconfig.string('''
...     <configure xmlns:grok="http://namespaces.zope.org/grok">
...       <include package="grokcore.component" file="meta.zcml"/>
...       <grok:grok package="."
...                  exclude="file_*
...                           *asdf" />
...     </configure>''', context)
<zope.configuration.config.ConfigurationMachine ...>

"""

from zope.configuration import xmlconfig
from grokcore.component.tests.zcml import excludemanypkg

context = xmlconfig.ConfigurationMachine()
xmlconfig.registerCommonDirectives(context)
context.package = excludemanypkg
