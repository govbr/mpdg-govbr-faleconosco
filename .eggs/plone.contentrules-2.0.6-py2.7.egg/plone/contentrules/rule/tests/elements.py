"""Dummies used in ZCML tests
"""

from zope.interface import Interface, implementer
from zope import schema

from plone.contentrules.rule.interfaces import IRuleElementData

class ITestCondition(Interface):
    test = schema.TextLine(title=u"Test property")

@implementer(ITestCondition, IRuleElementData)
class TestCondition(object):
    test = u""

    summary = u"Test condition"
    element = u"test.condition"

class ITestAction(Interface):
    test = schema.TextLine(title=u"Test property")

@implementer(ITestAction, IRuleElementData)
class TestAction(object):
    test = u""

    summary = u"Test action"
    element = u"test.action"
