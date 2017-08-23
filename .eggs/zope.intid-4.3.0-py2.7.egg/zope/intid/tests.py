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
"""Tests for the unique id utility.
"""
import random
import struct
import unittest

import BTrees
from persistent import Persistent
from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection
from ZODB.POSException import POSKeyError
from zope.component import getSiteManager
from zope.component import provideAdapter
from zope.component import provideHandler
from zope.component import testing, eventtesting
from zope.component.interfaces import ISite, IComponentLookup
from zope.interface import implementer, Interface
from zope.interface.verify import verifyObject
from zope.keyreference.persistent import KeyReferenceToPersistent
from zope.keyreference.persistent import connectionOfPersistent
from zope.keyreference.interfaces import IKeyReference
from zope.location.interfaces import ILocation
from zope.site.hooks import setSite, setHooks, resetHooks
from zope.site.folder import rootFolder
from zope.site.site import SiteManagerAdapter, LocalSiteManager
from zope.traversing import api
from zope.traversing.testing import setUp as traversingSetUp
from zope.traversing.interfaces import ITraversable
from zope.container.traversal import ContainerTraversable
from zope.container.interfaces import ISimpleReadContainer

from zope.intid import IntIds, intIdEventNotify
from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IntIdMissingError, IntIdsCorruptedError, ObjectMissingError

# Local Utility Addition
def addUtility(sitemanager, name, iface, utility, suffix=''):
    """Add a utility to a site manager

    This helper function is useful for tests that need to set up utilities.
    """
    folder_name = (name or (iface.__name__ + 'Utility')) + suffix
    default = sitemanager['default']
    default[folder_name] = utility
    utility = default[folder_name]
    sitemanager.registerUtility(utility, iface, name)
    return utility


# setup siteManager
def createSiteManager(folder, setsite=False):
    if not ISite.providedBy(folder):
        folder.setSiteManager(LocalSiteManager(folder))
    if setsite:
        setSite(folder)
    return api.traverse(folder, "++etc++site")


@implementer(ILocation)
class P(Persistent):
    pass


class ConnectionStub(object):
    next = 1

    def db(self):
        return self

    database_name = 'ConnectionStub'

    def add(self, ob):
        ob._p_jar = self
        ob._p_oid = struct.pack(">I", self.next)
        self.next += 1

class POSKeyRaisingDict(object):

    def __getitem__(self, i):
        raise POSKeyError(i)

    def __delitem__(self, i):
        raise POSKeyError(i)

class ReferenceSetupMixin(object):
    """Registers adapters ILocation->IConnection and IPersistent->IReference"""

    def setUp(self):
        testing.setUp()
        eventtesting.setUp()
        traversingSetUp()
        setHooks()
        provideAdapter(ContainerTraversable,
                       (ISimpleReadContainer,), ITraversable)
        provideAdapter(SiteManagerAdapter, (Interface,), IComponentLookup)

        self.root = rootFolder()
        createSiteManager(self.root, setsite=True)

        provideAdapter(connectionOfPersistent, (IPersistent, ), IConnection)
        provideAdapter(
            KeyReferenceToPersistent, (IPersistent, ), IKeyReference)

    def tearDown(self):
        resetHooks()
        setSite()
        testing.tearDown()


class TestIntIds(ReferenceSetupMixin, unittest.TestCase):

    def setUp(self):
        super(TestIntIds, self).setUp()
        self.conn = ConnectionStub()

    def tearDown(self):
        self.conn = None
        super(TestIntIds, self).tearDown()

    def createIntIds(self):
        return IntIds()

    def _create_registered_obj(self):
        obj = P()
        self.conn.add(obj)
        return obj

    def test_interface(self):
        verifyObject(IIntIds, self.createIntIds())

    def test_non_keyreferences(self):
        u = self.createIntIds()
        obj = object()

        self.assertTrue(u.queryId(obj) is None)
        self.assertTrue(u.unregister(obj) is None)
        self.assertRaises(IntIdMissingError, u.getId, obj)

    def test_getObject_POSKeyError(self):
        u = self.createIntIds()
        u.refs = POSKeyRaisingDict()
        self.assertRaises(POSKeyError, u.getObject, 1)

    def test_getId_queryId_POSKeyError(self):
        u = self.createIntIds()
        u.ids = POSKeyRaisingDict()
        obj = self._create_registered_obj()
        self.assertRaises(POSKeyError, u.getId, obj)
        self.assertRaises(POSKeyError, u.queryId, obj)

    def test_unregister_POSKeyError_refs(self):
        u = self.createIntIds()
        obj = self._create_registered_obj()
        u.register(obj)

        u.refs = POSKeyRaisingDict()
        self.assertRaises(POSKeyError, u.unregister, obj)

    def test_unregister_POSKeyError_ids(self):
        u = self.createIntIds()
        obj = self._create_registered_obj()
        u.register(obj)

        u.ids = POSKeyRaisingDict()
        self.assertRaises(POSKeyError, u.unregister, obj)

    def test_general(self):
        u = self.createIntIds()
        obj = self._create_registered_obj()

        self.assertRaises(IntIdMissingError, u.getId, obj)
        self.assertRaises(IntIdMissingError, u.getId, P())

        self.assertIsNone(u.queryId(obj))
        self.assertIs(u.queryId(obj, self), self)
        self.assertIs(u.queryId(P(), self), self)
        self.assertIsNone(u.queryObject(42))
        self.assertIs(u.queryObject(42, obj), obj)

        uid = u.register(obj)
        self.assertIs(u.getObject(uid), obj)
        self.assertIs(u.queryObject(uid), obj)
        self.assertEqual(u.getId(obj), uid)
        self.assertEqual(u.queryId(obj), uid)

        uid2 = u.register(obj)
        self.assertEqual(uid, uid2)

        u.unregister(obj)
        self.assertRaises(ObjectMissingError, u.getObject, uid)
        self.assertRaises(IntIdMissingError, u.getId, obj)

        # Unregistering again fails
        self.assertRaises(IntIdMissingError, u.unregister, obj)

        # Let's manually generate corruption
        uid = u.register(obj)
        del u.refs[uid]

        self.assertRaises(IntIdsCorruptedError, u.unregister, obj)
        # But we can still ask for its id
        self.assertEqual(u.getId(obj), uid)

    def test_btree_long(self):
        # This is a somewhat arkward test, that *simulates* the border case
        # behaviour of the _generateId method
        u = self.createIntIds()
        maxint = u.family.maxint
        u._randrange = lambda x,y: maxint-1

        obj = self._create_registered_obj()

        uid = u.register(obj)
        self.assertEqual(maxint-1, uid)
        self.assertEqual(maxint, u._v_nextid)

        # The next chosen int is exactly the largest number possible that is
        # delivered by the randint call in the code
        obj = self._create_registered_obj()

        uid = u.register(obj)
        self.assertEqual(maxint, uid)
        # Make an explicit tuple here to avoid implicit type casts
        # by the btree code
        self.assertIn(maxint, tuple(u.refs.keys()))

        # _v_nextid is now set to None, since the last id generated was
        # maxint.
        self.assertEqual(u._v_nextid, None)
        # make sure the next uid generated is less than maxint
        obj = self._create_registered_obj()

        u._randrange = random.randrange
        uid = u.register(obj)
        self.assertLess(uid, maxint)

    def test_len_items(self):
        u = self.createIntIds()
        obj = self._create_registered_obj()

        self.assertEqual(len(u), 0)
        self.assertEqual(u.items(), [])
        self.assertEqual(list(u), [])

        uid = u.register(obj)
        ref = KeyReferenceToPersistent(obj)
        self.assertEqual(len(u), 1)
        self.assertEqual(u.items(), [(uid, ref)])
        self.assertEqual(list(u), [uid])

        obj2 = P()
        obj2.__parent__ = obj

        uid2 = u.register(obj2)
        ref2 = KeyReferenceToPersistent(obj2)
        self.assertEqual(len(u), 2)
        result = u.items()
        expected = [(uid, ref), (uid2, ref2)]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)
        result = list(u)
        expected = [uid, uid2]
        result.sort()
        expected.sort()
        self.assertEqual(result, expected)

        u.unregister(obj)
        u.unregister(obj2)
        self.assertEqual(len(u), 0)
        self.assertEqual(u.items(), [])

    def test_getenrateId(self):
        u = self.createIntIds()
        self.assertEqual(u._v_nextid, None)
        id1 = u._generateId()
        self.assertTrue(u._v_nextid is not None)
        id2 = u._generateId()
        self.assertTrue(id1 + 1, id2)
        u.refs[id2 + 1] = "Taken"
        id3 = u._generateId()
        self.assertNotEqual(id3, id2 + 1)
        self.assertNotEqual(id3, id2)
        self.assertNotEqual(id3, id1)


class TestSubscribers(ReferenceSetupMixin, unittest.TestCase):

    def setUp(self):
        from zope.site.folder import Folder

        ReferenceSetupMixin.setUp(self)

        sm = getSiteManager(self.root)
        self.utility = addUtility(sm, '1', IIntIds, IntIds())

        self.root['folder1'] = Folder()
        self.root._p_jar = ConnectionStub()
        self.root['folder1']['folder1_1'] = self.folder1_1 = Folder()
        self.root['folder1']['folder1_1']['folder1_1_1'] = Folder()

        sm1_1 = createSiteManager(self.folder1_1)
        self.utility1 = addUtility(sm1_1, '2', IIntIds, IntIds())
        provideHandler(intIdEventNotify)

    def test_removeIntIdSubscriber(self):
        from zope.lifecycleevent import ObjectRemovedEvent
        from zope.intid import removeIntIdSubscriber
        from zope.intid.interfaces import IIntIdRemovedEvent
        from zope.site.interfaces import IFolder
        parent_folder = self.root['folder1']['folder1_1']
        folder = self.root['folder1']['folder1_1']['folder1_1_1']
        id = self.utility.register(folder)
        id1 = self.utility1.register(folder)
        self.assertEqual(self.utility.getObject(id), folder)
        self.assertEqual(self.utility1.getObject(id1), folder)
        setSite(self.folder1_1)

        events = []
        objevents = []

        def appendObjectEvent(obj, event):
            objevents.append((obj, event))

        provideHandler(events.append, [IIntIdRemovedEvent])
        provideHandler(appendObjectEvent, [IFolder, IIntIdRemovedEvent])

        # Nothing happens for objects that can't be a keyreference
        removeIntIdSubscriber(self, None)
        self.assertEqual([], events)

        # This should unregister the object in all utilities, not just the
        # nearest one.
        removeIntIdSubscriber(folder, ObjectRemovedEvent(parent_folder))

        self.assertRaises(ObjectMissingError, self.utility.getObject, id)
        self.assertRaises(ObjectMissingError, self.utility1.getObject, id1)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].object, folder)
        self.assertEqual(events[0].original_event.object, parent_folder)

        self.assertEqual(len(objevents), 1)
        self.assertEqual(objevents[0][0], folder)
        self.assertEqual(objevents[0][1].object, folder)
        self.assertEqual(objevents[0][1].original_event.object, parent_folder)

        # Removing again will produce key errors, but those don't
        # propagate from the subscriber
        del events[:]
        del objevents[:]
        self.assertRaises(IntIdMissingError, self.utility.unregister, parent_folder)

        removeIntIdSubscriber(folder, ObjectRemovedEvent(parent_folder))
        # Note that even though we didn't remove it, we still sent an event...
        self.assertEqual(len(events), 1)


    def test_addIntIdSubscriber(self):
        from zope.lifecycleevent import ObjectAddedEvent
        from zope.intid import addIntIdSubscriber
        from zope.intid.interfaces import IIntIdAddedEvent
        from zope.site.interfaces import IFolder
        parent_folder = self.root['folder1']['folder1_1']
        folder = self.root['folder1']['folder1_1']['folder1_1_1']
        setSite(self.folder1_1)

        events = []
        objevents = []

        def appendObjectEvent(obj, event):
            objevents.append((obj, event))

        provideHandler(events.append, [IIntIdAddedEvent])
        provideHandler(appendObjectEvent, [IFolder, IIntIdAddedEvent])

        # Nothing happens for objects that can't be a keyreference
        addIntIdSubscriber(self, None)
        self.assertEqual([], events)


        # This should register the object in all utilities, not just the
        # nearest one.
        addIntIdSubscriber(folder, ObjectAddedEvent(parent_folder))

        # Check that the folder got registered
        id = self.utility.getId(folder)
        id1 = self.utility1.getId(folder)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].original_event.object, parent_folder)
        self.assertEqual(events[0].object, folder)

        self.assertEqual(len(objevents), 1)
        self.assertEqual(objevents[0][1].original_event.object, parent_folder)
        self.assertEqual(objevents[0][1].object, folder)
        self.assertEqual(objevents[0][0], folder)

        idmap = events[0].idmap
        self.assertTrue(idmap is objevents[0][1].idmap)
        self.assertEqual(len(idmap), 2)
        self.assertEqual(idmap[self.utility], id)
        self.assertEqual(idmap[self.utility1], id1)

class TestIntIds64(TestIntIds):

    def createIntIds(self):
        return IntIds(family=BTrees.family64)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIntIds))
    suite.addTest(unittest.makeSuite(TestIntIds64))
    suite.addTest(unittest.makeSuite(TestSubscribers))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
