# -*- coding: utf-8 -*-
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

import unittest


class MensagemAddViewTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_view_mensagemadd(self):
        view = self.portal.restrictedTraverse('@@add-mensagem')
        self.assertTrue(view)
