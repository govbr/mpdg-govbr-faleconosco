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
from Acquisition import aq_base
from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from AccessControl import Unauthorized
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING
import transaction
from mpdg.govbr.faleconosco.config import KEY_CONFIRMA, EMAIL_FALE_LINK
from mpdg.govbr.faleconosco.mailer import simple_send_mail
from mpdg.govbr.faleconosco.utils import prepare_email_message
from mpdg.govbr.faleconosco.browser.utilities import transform_message, get_fale_config


class FaleConoscoForm(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer["request"]
        alsoProvides(self.request, IFormLayer)
        """Definição codigo email"""
        # self.app = self.layer['app']
        # self.portal._original_MailHost = self.portal.MailHost
        # self.portal.MailHost = mailhost = MockMailHost('MailHost')
        # sm = getSiteManager(context=self.portal)
        # sm.unregisterUtility(provided=IMailHost)
        # sm.registerUtility(mailhost, provided=IMailHost)
        
        # self.portal.email_from_address = 'govbr@planejamento.gov.br'
        # transaction.commit()
        # self.request = self.layer["request"]
       

        # # self.view = FaleConoscoForm(self.portal, self.request, self.views)
        # self.request.form['form','form-widgets-email','form-widgets-assunto','form-widgets-mensagem'] = '123123132131'
        # self.view = FaleConoscoForm(self.portal, self.request)
   
    """Testa se a view está funcionando corretamente"""
    def test_fale_conosco(self):
         view = self.portal.restrictedTraverse('@@fale-conosco')
         self.assertTrue(view)

    """Verifica se o objeto fale conosco existe na dentro da pasta fale conosco"""
    def test_object_in_folder(self):
         self.assertFalse('fale-conosco' in  self.portal.objectIds('@@fale-conosco'))

    # def test_view_is_protected(self):
    #      """Somente admin do fale ou manager pode acessar essa view"""
    #      self.assertRaises(Unauthorized, self.view.update)

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





    """Verifica se o buttão enviar está enviando dados corretamente"""
    # def test_form_button(self):
    #     button = self.portal.getControl(name="Enviar")                                                                                                                                                                                                    
    #     button.click()

    # """teste SAÍDA Enviar email quando o usuário preenche o formulário"""
    # def tearDown(self):
    #     self.portal.MailHost = self.portal._original_MailHost
    #     sm = getSiteManager(context=self.portal)
    #     sm.unregisterUtility(provided=IMailHost)
    #     sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)
     
    """teste SAÍDA Enviar email quando o usuário preenche o formulário"""
    # def test_mockmailhost_setting(self):
    #     #open contact form
    #     browser = Browser(self.app)
    #     browser.open('http://localhost:8080/Plone/fale-conosco/@@fale-conosco'
    #     # Now fill in the form:

    #     form = browser.getForm(name='')
    #     form.getControl(name='nome').value = 'T\xc3\xa4st user'
    #     form.getControal(name='email').value = 'test@plone.test'
    #     form.getControl(name='assunto').value = 'Saluton amiko to\xc3\xb1o'
    #     form.getControl(name='mensagem').value = 'Message with funny chars: \xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xb1.'

    #     # And submit it:
    #     form.submit()
    #     self.assertEqual(browser.url, 'http://localhost:8080/Plone/fale-conosco/@@fale-conosco')
    #     self.assertIn('E-mail enviado', browser.contents)

    #     # As part of our test setup, we replaced the original MailHost with our
    #     # own version.  Our version doesn't mail messages, it just collects them
    #     # in a list called ``messages``:
    #     mailhost = self.portal.MailHost
    #     self.assertEqual(len(mailhost.messages), 1)
    #     msg = message_from_string(mailhost.messages[0])

    #     self.assertEqual(msg['MIME-Version'], '1.0')
    #     self.assertEqual(msg['Content-Type'], 'text/plain; charset="utf-8"')
    #     self.assertEqual(msg['Content-Transfer-Encoding'], 'quoted-printable')
    #     self.assertEqual(msg['Subject'], '=?utf-8?q?Saluton_amiko_to=C3=B1o?=')
    #     self.assertEqual(msg['From'], 'govbr@planejamento.gov.br')
    #     self.assertEqual(msg['To'], 'govbr@planejamento.gov.br')
    #     msg_body = msg.get_payload()
    #     self.assertIn(u'Message with funny chars: =C3=A1=C3=A9=C3=AD=C3=B3=C3=BA=C3=B1',
    #                   msg_body)