# -*- coding: utf-8 -*-
from plone.app.customerize.tool import ViewTemplateContainer
from Products.CMFCore.utils import ToolInit


def initialize(context):
    """ initialize function called when used as a zope2 product """

    ToolInit('plone.app.customerize',
             tools=(ViewTemplateContainer,),
             icon='tool.gif',
             ).initialize(context)
