##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Grok test helpers
"""
import grokcore.component
from zope.configuration.config import ConfigurationMachine
from martian import scan
from grokcore.component import zcml

def grok(*module_names):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.compat', config)
    zcml.do_grok('grokcore.component.meta', config)
    for module_name in module_names:
        zcml.do_grok(module_name, config)
    config.execute_actions()

def grok_component(name, component,
                   context=None, module_info=None, templates=None, dotted_name=None):
    if module_info is None:
        if dotted_name is None:
            dotted_name = getattr(component, '__grok_module__', None)
            if dotted_name is None:
                dotted_name = getattr(component, '__module__', None)
            module_info = scan.module_info_from_dotted_name(dotted_name)
        module_info = scan.module_info_from_dotted_name(dotted_name)

    module = module_info.getModule()
    if context is not None:
        grokcore.component.context.set(module, context)
    if templates is not None:
        module.__grok_templates__ = templates
    config = ConfigurationMachine()
    result = zcml.the_multi_grokker.grok(name, component,
                                         module_info=module_info,
                                         config=config)
    config.execute_actions()    
    return result
