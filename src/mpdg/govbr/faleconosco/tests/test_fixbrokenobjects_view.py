# -*- coding: utf-8 -*-
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

import unittest

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles


class FixBrokenObjectsViewTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_view_fixbrokenobjects(self):
        view = self.portal.restrictedTraverse('@@fixbrokenobjects')
        self.assertTrue(view)
