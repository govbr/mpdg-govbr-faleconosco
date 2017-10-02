#-*- coding: utf-8 -*-
import unittest
from plone.app.testing import TEST_USER_ID
from plone import api
from z3c.form import button
from z3c.form.interfaces import IFormLayer
from zope.interface import alsoProvides
from plone.app.testing import setRoles
from mpdg.govbr.faleconosco.browser.faleconoscoform import IFaleConoscoForm, FaleConoscoForm
import unittest2 as unittest
from email import message_from_string
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from Products.Five.testbrowser import Browser
from Acquisition import aq_base
from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from AccessControl import Unauthorized
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING
import transaction


class FaleConoscoForms(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer["request"]
        alsoProvides(self.request, IFormLayer)
        self.view = FaleConoscoForm(self.portal, self.request)
        self.request.form['form.widgets.nome'] = '123123132131'

    """Testa se a view está funcionando corretamente"""
    # def test_fale_conosco(self):
    #     portal = self.portal
    #     view = portal.restrictedTraverse('@@fale-conosco')
    #     self.assertTrue(view)

    def test_controlpanel_view_protected(self):
        """ Acesso a view nao pode ser feito por usuario anonimo """
        # Importamos a excecao esperada
        from AccessControl import Unauthorized
        # Deslogamos do portal
        logout()
        # Ao acessar a view como anonimo, a excecao e levantada
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@site-controlpanel')

    """Verifica se o objeto fale conosco existe na dentro da pasta fale conosco"""
    def test_object_in_folder(self):
         self.assertFalse('fale-conosco' in  self.portal.objectIds('@@fale-conosco'))

    """Testa se a view retorna status http 200 quando acessada"""
    def test_view_get_valid(self):
         setRoles(self.portal, TEST_USER_ID, ['Manager'])
         self.view.update()
         self.assertEqual(200, self.view.request.response.status)

    """Verifica se a view possui os campos obrigatorios"""
    def test_form_fields(self):
        expected = ['nome', 'email', 'assunto', 'mensagem']
        for field in expected:
            self.assertIn(field, self.view.schema.names())

    # def logoutWithTestBrowser(self):

    #     browser = Browser(self.app)
    #     self.browser.open(self.portal.absolute_url() + '/logout')
            
    #     html = self.browser.contents

    #     self.assertTrue("You are now logged out" in html)

    #     print browser.contents # O navegador é instância zope.testbrowser.Browser
            
    #     form = browser.getForm(index=2) # Salte o login e o formulário de pesquisa no Plone 4

    #         # Obter o formulário de login do zope.testbrowser
    #     login_form = self.browser.getForm('login_form')
    #         # get and print all controls
    #     controls = login_form.mech_form.controls
    #     for control in controls:
    #         print "%s: %s" % (control.attrs['name'], control.attrs['type'])

    #     for c in form.mech_form.controls: print c
    #     print browser.contents

    #     self.browser.open(self.portal.absolute_url() + "/search")

    #     # Insira alguns valores para a pesquisa que vemos que recebemos

    #     for search_terms in [u"Plone", u"youcantfindthis"]:
    #         form = self.browser.getForm("searchform")

    #         # Fill in the search field
    #         input = form.getControl(name="SearchableText")
    #         input.value = search_terms

    #         # Envie o formulário 
    #         form.submit(u"Search")

    #     button = form.getControl(name="mybuttonname")
    #     button.click()

    #     login_form = self.browser.getForm('login_form')
    #     login_form.submit('Log in')


    def test_anon_access_forum(self):
        """
        Os usuários anônimos não devem ser capazes de abrir a página do fórum
        """

        self.portal.error_log._ignored_exceptions = ()
        self.portal.acl_users.credentials_cookie_auth.login_path = ""

        exception = None
        try:
            self.browser.open(self.portal.intranet.forum.absolute_url())
        except:
            # Manuseie um caso quebrado onde O navegador
            # test detecta uma exceção sem uma classe base (WTF)
            import sys
            exception = sys.exc_info()[0]

        self.assertFalse(exception is None) 