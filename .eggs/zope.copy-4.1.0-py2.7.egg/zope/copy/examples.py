##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
""" Make example classes available at module scope.
"""
import zope.location.location


class Demo(object):

    _frozen = None

    def isFrozen(self):
        return self._frozen is not None

    def freeze(self):
        self._frozen = Data()


class Data(object):
    pass


class Subobject(zope.location.location.Location):

    def __init__(self):
        self.counter = 0

    def __call__(self):
        res = self.counter
        self.counter += 1
        return res


class Something(object):
    pass


class Other(object):
    root = object()  # immutable
    __name__ = property(lambda _self: 'something')
    __parent__ = property(lambda self: self.__class__.root)
