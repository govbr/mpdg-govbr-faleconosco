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
"""Unique id utility.

This utility assigns unique integer ids to objects and allows lookups
by object and by id.

This functionality can be used in cataloging.
"""
import random

import BTrees
from persistent import Persistent
from zope.component import adapter, getAllUtilitiesRegisteredFor, handle
from zope.event import notify
from zope.interface import implementer
from zope.keyreference.interfaces import IKeyReference, NotYet
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.location.interfaces import ILocation
from zope.location.interfaces import IContained
from zope.security.proxy import removeSecurityProxy

from zope.intid.interfaces import IIntIds, IIntIdEvent
from zope.intid.interfaces import IntIdAddedEvent, IntIdRemovedEvent
from zope.intid.interfaces import IntIdMissingError, IntIdsCorruptedError, ObjectMissingError

try:
    # POSKeyError is a subclass of KeyError; in the cases where we
    # catch KeyError for an item missing from a BTree, we still
    # want to propagate this exception that indicates a corrupt database
    # (as opposed to a corrupt IntIds)
    from ZODB.POSException import POSKeyError as _POSKeyError
except ImportError: # pragma: no cover (we run tests with ZODB installed)
    # In practice, ZODB will probably be installed. But if not,
    # then POSKeyError can never be generated, so use a unique
    # exception that we'll never catch.
    class _POSKeyError(BaseException):
        pass

@implementer(IIntIds, IContained)
class IntIds(Persistent):
    """This utility provides a two way mapping between objects and
    integer ids.

    IKeyReferences to objects are stored in the indexes.
    """

    __parent__ = __name__ = None

    _v_nextid = None

    _randrange = random.randrange

    family = BTrees.family32

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.ids = self.family.OI.BTree()
        self.refs = self.family.IO.BTree()

    def __len__(self):
        return len(self.ids)

    def items(self):
        return list(self.refs.items())

    def __iter__(self):
        return self.refs.iterkeys()

    def getObject(self, id):
        try:
            return self.refs[id]()
        except _POSKeyError:
            raise
        except KeyError:
            raise ObjectMissingError(id)

    def queryObject(self, id, default=None):
        r = self.refs.get(id)
        if r is not None:
            return r()
        return default

    def getId(self, ob):
        try:
            key = IKeyReference(ob)
        except (NotYet, TypeError, ValueError):
            raise IntIdMissingError(ob)

        try:
            return self.ids[key]
        except _POSKeyError:
            raise
        except KeyError:
            raise IntIdMissingError(ob)

    def queryId(self, ob, default=None):
        try:
            return self.getId(ob)
        except _POSKeyError:
            raise
        except KeyError:
            return default

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        nextid = getattr(self, '_v_nextid', None)
        while True:
            if nextid is None:
                nextid = self._randrange(0, self.family.maxint)
            uid = nextid
            if uid not in self.refs:
                nextid += 1
                if nextid > self.family.maxint:
                    nextid = None
                self._v_nextid = nextid
                return uid
            nextid = None

    def register(self, ob):
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        key = IKeyReference(ob)

        if key in self.ids:
            return self.ids[key]
        uid = self._generateId()
        self.refs[uid] = key
        self.ids[key] = uid
        return uid

    def unregister(self, ob):
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        key = IKeyReference(ob, None)
        if key is None:
            return

        try:
            uid = self.ids[key]
        except _POSKeyError:
            raise
        except KeyError:
            raise IntIdMissingError(ob)

        try:
            del self.refs[uid]
        except _POSKeyError:
            raise
        except KeyError:
            # It was in self.ids, but not self.refs. Something is corrupted.
            # We've always let this KeyError propagate, before cleaning up self.ids,
            # meaning that getId(ob) will continue to work, but getObject(uid) will not.
            raise IntIdsCorruptedError(ob, uid)
        del self.ids[key]

def _utilities_and_key(ob):
    utilities = tuple(getAllUtilitiesRegisteredFor(IIntIds))
    return utilities, IKeyReference(ob, None) if utilities else None

@adapter(ILocation, IObjectRemovedEvent)
def removeIntIdSubscriber(ob, event):
    """A subscriber to ObjectRemovedEvent

    Removes the unique ids registered for the object in all the unique
    id utilities.
    """
    utilities, key = _utilities_and_key(ob)
    if not utilities or key is None:
        # Unregister only objects that adapt to key reference
        return
    # Notify the catalogs that this object is about to be removed.
    notify(IntIdRemovedEvent(ob, event))
    for utility in utilities:
        try:
            utility.unregister(key)
        except KeyError:
            # Silently ignoring all kinds corruption here
            pass

@adapter(ILocation, IObjectAddedEvent)
def addIntIdSubscriber(ob, event):
    """A subscriber to ObjectAddedEvent

    Registers the object added in all unique id utilities and fires
    an event for the catalogs.
    """
    utilities, key = _utilities_and_key(ob)
    if not utilities or key is None:
        # Register only objects that adapt to key reference
        return
    idmap = {}
    for utility in utilities:
        idmap[utility] = utility.register(key)
    # Notify the catalogs that this object was added.
    notify(IntIdAddedEvent(ob, event, idmap))

@adapter(IIntIdEvent)
def intIdEventNotify(event):
    """Event subscriber to dispatch IntIdEvent to interested adapters."""
    handle(event.object, event)
