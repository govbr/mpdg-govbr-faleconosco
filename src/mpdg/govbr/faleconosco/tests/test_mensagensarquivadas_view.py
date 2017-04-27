#-*- coding: utf-8 -*-
import unittest
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING


class MensagensArquivadasViewTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_view_mensagensarquivadas(self):
        view = self.portal.restrictedTraverse('@@mensagens-arquivadas-admin')
        self.assertTrue(view)
