##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Grok interfaces
"""

from zope import interface


class IBaseClasses(interface.Interface):
    """grokcore.annotation base classes.
    """
    Annotation = interface.Attribute(
        "Base class for persistent annotations.")

    LazyAnnotation = interface.Attribute(
        "Base class for lazily persisted annotations.")

    LazyAnnotationProperty = interface.Attribute(
        "Base class for schema attributes defined on lazy annotations.")


class IAnnotationFactory(interface.Interface):
    factory = interface.Attribute('Class to create a new annotation')
    name = interface.Attribute('Name of the annotation')

    def query(context):
        """Return the existing annotation or None if no annotaion
        was created before.
        """

    def delete(context):
        """Delete the existing annotation on the context.
        """

    def __call__(context):
        """Return the existing annotation or create a new one.
        """


class IGrokcoreAnnotationAPI(IBaseClasses):
    """grokcore.annotation API description.
    """
    queryAnnotation = interface.Attribute('Query an annotation or return None')
    deleteAnnotation = interface.Attribute('Delete an annotation if it exists')
