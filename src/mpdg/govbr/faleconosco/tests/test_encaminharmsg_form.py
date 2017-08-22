#-*- coding: utf-8 -*-
import unittest
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING
from z3c.form.interfaces import IFormLayer
from zope.interface import alsoProvides
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from AccessControl import Unauthorized

from mpdg.govbr.faleconosco.browser.encaminharmensagemview import IEncaminharMensagemForm, EncaminharMensagemView


class EncaminharMsgFormTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer["request"]
        alsoProvides(self.request, IFormLayer) #suitable for testing z3c.form views
        group = api.group.create(groupname='adm-fale-conosco')

        self.request.form['form.widgets.uids'] = '123123132131'
        self.view = EncaminharMensagemView(self.portal, self.request)


    def test_view_is_protected(self):
        """Somente admin do fale ou manager pode acessar essa view"""
        self.assertRaises(Unauthorized, self.view.update)

    def test_view_get_valid(self):
        """Testa se a view retorna status http 200 quando acessada"""
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.view.update()
        self.assertEqual(200, self.view.request.response.status)

    def test_form_fields(self):
        """Verifica se a view possui os campos obrigatorios"""
        expected = ['uids', 'usuario', 'mensagem']
        for field in expected:
            self.assertIn(field, self.view.schema.names())

     # """Verifica se o buttão enviar está enviando dados corretamente """
     # def test_form_button(self):
     #     button = self.portal.getControl(name="Enviar")
     #     button.click()
    

    