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
"""Base classes for Grok application components.

"""

import persistent
import zope.annotation.interfaces
import zope.cachedescriptors.property

from zope.interface import implementer
from zope.location import Location
from zope.annotation.interfaces import IAnnotations
from grokcore.annotation.interfaces import IAnnotationFactory

_marker = object()


class LazyAnnotationProperty(object):

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if not isinstance(inst, LazyAnnotation):
            return self

        value = inst._load(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        if not isinstance(inst, LazyAnnotation):
            raise ValueError(self.__name, 'invalid context')

        field = self.__field.bind(inst)
        if field.readonly:
            raise ValueError(self.__name, 'field is readonly')
        field.validate(value)
        inst._store(self.__name, value)

    def __getattr__(self, name):
        return getattr(self.__field, name)


class Storage(persistent.Persistent):
    pass


class LazyAnnotation(Location):

    @zope.cachedescriptors.property.Lazy
    def storage(self):
        annotations = IAnnotations(self.__parent__)
        return annotations.get(self.__name__)

    def _store(self, key, value):
        storage = self.storage
        if storage is None:
            annotations = IAnnotations(self.__parent__)
            annotations[self.__name__] = storage = Storage()
            self.__dict__['storage'] = storage
        setattr(storage, key, value)

    def _load(self, key, default):
        storage = self.storage
        if storage is None:
            return default
        return getattr(storage, key, default)


@implementer(IAnnotationFactory)
class LazyAnnotationFactory(object):

    def __init__(self, factory, name):
        self.factory = factory
        self.name = name

    def query(self, context):
        annotations = IAnnotations(context)
        if self.name in annotations:
            return self(context)
        return None

    def delete(self, context):
        annotations = IAnnotations(context)
        if self.name in annotations:
            del annotations[self.name]
            return True
        return False

    def __call__(self, context):
        result = self.factory()
        result.__parent__ = context
        result.__name__ = self.name
        return result
