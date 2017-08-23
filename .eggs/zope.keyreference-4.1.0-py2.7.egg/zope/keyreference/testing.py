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
"""Testing components
"""
import zope.interface
import zope.component
import zope.keyreference.interfaces

@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zope.keyreference.interfaces.IKeyReference)
class SimpleKeyReference(object):
    """An IReference for all objects. This implementation is *not* ZODB safe.
    """

    key_type_id = 'zope.app.keyreference.simple'

    def __init__(self, object):
        self.object = object

    def __call__(self):
        return self.object

    def __hash__(self):
        return hash(self.object)

    def _get_cmp_keys(self, other):
        if self.key_type_id == other.key_type_id:
            return hash(self.object), hash(other)

        return self.key_type_id, other.key_type_id

    # Py3: For Python 2 BBB.
    def __cmp__(self, other):
        return cmp(*self._get_cmp_keys(other))

    def __eq__(self, other):
        a, b = self._get_cmp_keys(other)
        return a == b

    def __lt__(self, other):
        a, b = self._get_cmp_keys(other)
        return a < b

    def __ne__(self, other):
        a, b = self._get_cmp_keys(other)
        return a != b

    def __gt__(self, other):
        a, b = self._get_cmp_keys(other)
        return a > b

    def __le__(self, other):
        a, b = self._get_cmp_keys(other)
        return a <= b

    def __ge__(self, other):
        a, b = self._get_cmp_keys(other)
        return a >= b
