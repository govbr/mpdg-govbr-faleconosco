# -*- coding: utf-8 -*-
from mpdg.govbr.faleconosco.browser.desarquivarmensagem import DesarquivarMensagemView
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING
from plone import api

import unittest


class DesarquivarMensagemViewTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.view = DesarquivarMensagemView(self.portal, self.request)
        api.group.create(groupname='adm-fale-conosco')

    def test_view_desarquivar_mensagem(self):
        view = self.portal.restrictedTraverse('@@desarquivar-mensagem')
        self.assertTrue(view)

    """Somente admin do fale ou manager pode acessar essa view"""
    # def test_view_is_protected(self):
    #     self.assertRaises(Unauthorized, self.view.update)

    """ buttão enviar está enviando o conteúdo """

    # def test_buttão_view(self):
    #     button = form.getControl(name="Enviar")
    #     button.click()
