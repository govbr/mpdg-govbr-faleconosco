#-*- coding: utf-8 -*-
import unittest
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING
from AccessControl import Unauthorized
from mpdg.govbr.faleconosco.browser.faleconoscoadminview import FaleConoscoAdminView
from plone import api



class FaleConoscoAdminViewTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer["request"]
        self.view = FaleConoscoAdminView(self.portal, self.request)
        group = api.group.create(groupname='adm-fale-conosco')

    def test_view_faleconosco_admin(self):
        view = self.portal.restrictedTraverse('@@fale-conosco-admin')
        self.assertTrue(view)

    """Somente admin do fale ou manager pode acessar essa view"""
    def test_view_is_protected(self):
        self.assertRaises(Unauthorized, self.view.update)