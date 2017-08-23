##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Attribute Annotations implementation"""
import logging

try:
    from BTrees.OOBTree import OOBTree as _STORAGE
except ImportError: # pragma: no cover
    logging.getLogger(__name__).warning(
        'BTrees not available: falling back to dict for attribute storage')
    _STORAGE = dict

from zope import component, interface
from zope.annotation import interfaces

from collections import MutableMapping as DictMixin

_EMPTY_STORAGE = _STORAGE()

@interface.implementer(interfaces.IAnnotations)
@component.adapter(interfaces.IAttributeAnnotatable)
class AttributeAnnotations(DictMixin):
    """Store annotations on an object

    Store annotations in the `__annotations__` attribute on a
    `IAttributeAnnotatable` object.
    """

    def __init__(self, obj, context=None):
        self.obj = obj

    def __bool__(self):
        return bool(getattr(self.obj, '__annotations__', 0))

    __nonzero__ = __bool__

    def get(self, key, default=None):
        """See zope.annotation.interfaces.IAnnotations"""
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return annotations.get(key, default)

    def __getitem__(self, key):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return annotations[key]

    def keys(self):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return annotations.keys()

    def __iter__(self):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return iter(annotations)

    def __len__(self):
        annotations = getattr(self.obj, '__annotations__', _EMPTY_STORAGE)
        return len(annotations)

    def __setitem__(self, key, value):
        """See zope.annotation.interfaces.IAnnotations"""
        try:
            annotations = self.obj.__annotations__
        except AttributeError:
            annotations = self.obj.__annotations__ = _STORAGE()

        annotations[key] = value

    def __delitem__(self, key):
        """See zope.app.interfaces.annotation.IAnnotations"""
        try:
            annotation = self.obj.__annotations__
        except AttributeError:
            raise KeyError(key)

        del annotation[key]
