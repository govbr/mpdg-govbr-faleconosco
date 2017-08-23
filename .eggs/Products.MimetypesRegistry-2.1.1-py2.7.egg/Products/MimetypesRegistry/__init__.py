# -*- coding: utf-8 -*-
from AccessControl.SecurityInfo import allow_class
from AccessControl.SecurityInfo import allow_module
from Products.MimetypesRegistry import MimeTypesRegistry
from Products.MimetypesRegistry.interfaces import MimeTypeException


# remove when Archetypes are removed:
allow_module('Products.MimetypesRegistry.common')
allow_class(MimeTypeException)
# end remove


def initialize(context):
    from Products.CMFCore import utils
    utils.ToolInit(
        'MimetypesRegistry Tool',
        tools=(MimeTypesRegistry.MimeTypesRegistry, ),
        icon='tool.gif',
    ).initialize(context)
