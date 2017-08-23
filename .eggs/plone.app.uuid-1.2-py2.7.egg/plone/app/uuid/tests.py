# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.uuid.testing import PLONE_APP_UUID_FUNCTIONAL_TESTING
from plone.app.uuid.testing import PLONE_APP_UUID_INTEGRATION_TESTING

import unittest


class IntegrationTestCase(unittest.TestCase):
    layer = PLONE_APP_UUID_INTEGRATION_TESTING

    def test_assignment(self):
        from plone.uuid.interfaces import IUUID

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')

        d1 = portal['d1']
        uuid = IUUID(d1)

        self.assertTrue(isinstance(uuid, str))

    def test_search(self):
        from plone.uuid.interfaces import IUUID

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')
        portal.invokeFactory('Document', 'd2')

        d1 = portal['d1']
        uuid = IUUID(d1)

        catalog = portal['portal_catalog']
        results = catalog(UID=uuid)

        self.assertEqual(1, len(results))
        self.assertEqual(uuid, results[0].UID)
        self.assertEqual('/'.join(d1.getPhysicalPath()), results[0].getPath())

    def test_uuidToPhysicalPath(self):
        from plone.uuid.interfaces import IUUID
        from plone.app.uuid.utils import uuidToPhysicalPath

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')
        portal.invokeFactory('Document', 'd2')

        d1 = portal['d1']
        uuid = IUUID(d1)

        self.assertEqual('/'.join(d1.getPhysicalPath()),
                         uuidToPhysicalPath(uuid))

    def test_uuidToURL(self):
        from plone.uuid.interfaces import IUUID
        from plone.app.uuid.utils import uuidToURL

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')
        portal.invokeFactory('Document', 'd2')

        d1 = portal['d1']
        uuid = IUUID(d1)

        self.assertEqual(d1.absolute_url(), uuidToURL(uuid))

    def test_uuidToObject(self):
        from Acquisition import aq_base
        from plone.uuid.interfaces import IUUID
        from plone.app.uuid.utils import uuidToObject

        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')
        portal.invokeFactory('Document', 'd2')

        d1 = portal['d1']
        uuid = IUUID(d1)

        self.assertEqual(aq_base(d1), aq_base(uuidToObject(uuid)))


class FunctionalTestCase(unittest.TestCase):

    layer = PLONE_APP_UUID_FUNCTIONAL_TESTING

    def test_uuid_view(self):

        from plone.uuid.interfaces import IUUID

        portal = self.layer['portal']
        app = self.layer['app']

        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')

        d1 = portal['d1']
        uuid = IUUID(d1)

        import transaction
        transaction.commit()

        from plone.testing.z2 import Browser
        browser = Browser(app)
        browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(TEST_USER_ID, TEST_USER_PASSWORD, )
        )

        browser.open('{0}/@@uuid'.format(d1.absolute_url()))
        self.assertEqual(uuid, browser.contents)

    def test_redirect_to_uuid_view(self):
        from plone.uuid.interfaces import IUUID

        portal = self.layer['portal']
        app = self.layer['app']

        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')
        portal.invokeFactory('Document', 'd2')

        d1 = portal['d1']
        uuid = IUUID(d1)

        import transaction
        transaction.commit()

        from plone.testing.z2 import Browser
        browser = Browser(app)
        browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(TEST_USER_ID, TEST_USER_PASSWORD,)
        )

        url = '{0}/@@redirect-to-uuid/{1}'
        browser.open(url.format(portal.absolute_url(), uuid,))
        self.assertEqual(d1.absolute_url(), browser.url)

    def test_redirect_to_uuid_invalid_uuid(self):
        portal = self.layer['portal']
        app = self.layer['app']

        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Document', 'd1')
        portal.invokeFactory('Document', 'd2')

        import transaction
        transaction.commit()

        from plone.testing.z2 import Browser
        browser = Browser(app)
        browser.handleErrors = False
        browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(TEST_USER_ID, TEST_USER_PASSWORD, )
        )

        url = '{0}/@@redirect-to-uuid/gibberish'
        from zope.publisher.interfaces import NotFound
        with self.assertRaises(NotFound):
            browser.open(url.format(portal.absolute_url()))
