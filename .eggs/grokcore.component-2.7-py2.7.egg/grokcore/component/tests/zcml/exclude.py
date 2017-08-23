"""
It allows to exclude a single package or module from beeing grokked.

There is a NameError in `.excludepkg.sample` which is raised when this
module is not excluded:

>>> xmlconfig.string('''
...     <configure xmlns:grok="http://namespaces.zope.org/grok">
...       <include package="grokcore.component" file="meta.zcml"/>
...       <grok:grok package="." />
...     </configure>''', context)
Traceback (most recent call last):
ZopeXMLConfigurationError: File "<string>", line 4.6-4.31
    NameError: name 'asdf' is not defined

Excluding `.excludepkg.sample` via ZCML allows to successfully grok the
module:

>>> xmlconfig.string('''
...     <configure xmlns:grok="http://namespaces.zope.org/grok">
...       <include package="grokcore.component" file="meta.zcml"/>
...       <grok:grok package="."
...                  exclude="sample" />
...     </configure>''', context)
<zope.configuration.config.ConfigurationMachine ...>

"""

from zope.configuration import xmlconfig
from grokcore.component.tests.zcml import excludepkg

context = xmlconfig.ConfigurationMachine()
xmlconfig.registerCommonDirectives(context)
context.package = excludepkg
