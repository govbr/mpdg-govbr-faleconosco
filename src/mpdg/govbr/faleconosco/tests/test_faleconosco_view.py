#-*- coding: utf-8 -*-
import unittest as unittest
from plone import api
from z3c.form import button
from z3c.form.interfaces import IFormLayer
from zope.interface import alsoProvides
from plone.app.testing import setRoles

from email import message_from_string
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from plone.testing.z2 import Browser

from Acquisition import aq_base
from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from AccessControl import Unauthorized

import transaction

from mpdg.govbr.faleconosco.config import KEY_CONFIRMA, EMAIL_FALE_LINK
from mpdg.govbr.faleconosco.mailer import simple_send_mail
from mpdg.govbr.faleconosco.utils import prepare_email_message
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING


class FaleConoscoForm(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        self.portal.email_from_address = 'govbr@planejamento.gov.br'
        transaction.commit()

        alsoProvides(self.request, IFormLayer)
   
    """Testa se a view está funcionando corretamente"""
    def test_fale_conosco(self):
         view = self.portal.restrictedTraverse('@@fale-conosco')
         self.assertTrue(view)

    """Verifica se o objeto fale conosco existe na dentro da pasta fale conosco"""
    def test_object_in_folder(self):
         self.assertFalse('fale-conosco' in  self.portal.objectIds('@@fale-conosco'))

    # """Testa se a view retorna status http 200 quando acessada"""
    # def test_view_get_valid(self):
    #      setRoles(self.portal, TEST_USER_ID, ['Manager'])
    #      self.view.update()
    #      self.assertEqual(200, self.view.request.response.status)

    # """Verifica se a view possui os campos obrigatorios"""
    # def test_form_fields(self):
    #     expected = ['nome', 'email', 'assunto', 'mensagem']
    #     for field in expected:
    #         self.assertIn(field, self.field.schema.names())



    # def test_controlpanel_view_protected(self):
    #     """ Acesso a view nao pode ser feito por usuario anonimo """
    #     # Importamos a excecao esperada
    #     from AccessControl import Unauthorized
    #     # Deslogamos do portal
    #     logout()
    #     # Ao acessar a view como anonimo, a excecao e levantada
    #     self.assertRaises(Unauthorized,
    #                       self.portal.restrictedTraverse,
    #                       '@@site-controlpanel')
    

    # """teste SAÍDA Enviar email quando o usuário preenche o formulário"""
    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)

    """teste SAÍDA Enviar email quando o usuário preenche o formulário"""

    def test_mockmailhost_setting(self):
        #Formulário de contato aberto
        browser = Browser(self.app)
        browser.open('http://nohost/plone/contact-info')
        # Agora preencha o formulário:
        # import pdb; pdb.set_trace()
        form = browser.getForm(name='feedback_form')
        form.getControl(name='sender_fullname').value = 'T\xc3\xa4st user'
        form.getControl(name='sender_from_address').value = 'test@plone.test'
        form.getControl(name='subject').value = 'Saluton amiko to\xc3\xb1o'
        form.getControl(name='message').value = 'Message with funny chars: \xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xb1.'

        # envie-o:
        form.submit()
        self.assertEqual(browser.url, 'http://nohost/plone/contact-info')
        self.assertIn('Mail sent', browser.contents)

        # Como parte da nossa configuração de teste, substituímos o MailHost original por nosso
        #Própria versão. Nossa versão não envia mensagens, apenas as coleta
        #Em uma lista chamada `` messages``:


        mailhost = self.portal.MailHost
        self.assertEqual(len(mailhost.messages), 1)
        msg = message_from_string(mailhost.messages[0])

        self.assertEqual(msg['MIME-Version'], '1.0')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="utf-8"')
        self.assertEqual(msg['Content-Transfer-Encoding'], 'quoted-printable')
        self.assertEqual(msg['Subject'], '=?utf-8?q?Saluton_amiko_to=C3=B1o?=')
        self.assertEqual(msg['From'], 'govbr@planejamento.gov.br')
        self.assertEqual(msg['To'], 'govbr@planejamento.gov.br')
        msg_body = msg.get_payload()
        self.assertIn(u'Message with funny chars: =C3=A1=C3=A9=C3=AD=C3=B3=C3=BA=C3=B1',
                      msg_body)

    def logoutWithTestBrowser(self):

        browser = Browser(self.app)
        self.browser.open(self.portal.absolute_url() + '/logout')
            
        html = self.browser.contents

        self.assertTrue("You are now logged out" in html)

        print browser.contents # O navegador é instância zope.testbrowser.Browser
            
        form = browser.getForm(index=2) # Salte o login e o formulário de pesquisa no Plone 4

            # Obter o formulário de login do zope.testbrowser
        login_form = self.browser.getForm('login_form')
            # get and print all controls
        controls = login_form.mech_form.controls
        for control in controls:
            print "%s: %s" % (control.attrs['name'], control.attrs['type'])

        for c in form.mech_form.controls: print c
        print browser.contents

        self.browser.open(self.portal.absolute_url() + "/search")

        # Insira alguns valores para a pesquisa que vemos que recebemos

        for search_terms in [u"Plone", u"youcantfindthis"]:
            form = self.browser.getForm("searchform")

            # Fill in the search field
            input = form.getControl(name="SearchableText")
            input.value = search_terms

            # Envie o formulário 
            form.submit(u"Search")

        button = form.getControl(name="mybuttonname")
        button.click()

        login_form = self.browser.getForm('login_form')
        login_form.submit('Log in')

    def checkIsUnauthorized(self, url):
        """
        Verifique se o URL fornece resposta não autorizada.
        """

        import urllib2

        # Desativar redirecionamento no erro de segurança
        self.portal.acl_users.credentials_cookie_auth.login_path = ""

        # Desligar o rastreamento de exceção para depuração configurada em afterSetUp ()

        self.browser.handleErrors = True

        def raising(self, info):
            pass
        self.portal.error_log._ignored_exceptions = ("Unauthorized")
        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

        try:
            self.browser.open(url)
            raise AssertionError("No Unauthorized risen:" + url)
        except urllib2.HTTPError,  e:
            # Teste testbrowser
            # uses urlllib2 and will raise this exception
            self.assertEqual(e.code, 401, "Got HTTP response code:" + str(e.code))
        # Another example where test browser / Zope 2 publisher where invalidly handling Unauthorized exception:

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