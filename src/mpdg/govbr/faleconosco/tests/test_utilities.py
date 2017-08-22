#Pythonic libraries
import unittest2 as unittest
from email import message_from_string

#Plone
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from plone.testing.z2 import Browser

from Acquisition import aq_base
from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
import transaction

#hkl namespace
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING


class TestFluxoMensagensView(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        self.portal.email_from_address = 'govbr@planejamento.gov.br'
        transaction.commit()

    def tearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_mockmailhost_setting(self):
        #open contact form
        browser = Browser(self.app)
        browser.open('http://nohost/plone/contact-info')
        # Now fill in the form:

        form = browser.getForm(name='feedback_form')
        form.getControl(name='sender_fullname').value = 'T\xc3\xa4st user'
        form.getControl(name='sender_from_address').value = 'test@plone.test'
        form.getControl(name='subject').value = 'Saluton amiko to\xc3\xb1o'
        form.getControl(name='message').value = 'Message with funny chars: \xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xb1.'

        # And submit it:
        form.submit()
        self.assertEqual(browser.url, 'http://nohost/plone/contact-info')
        self.assertIn('Mail sent', browser.contents)

        # As part of our test setup, we replaced the original MailHost with our
        # own version.  Our version doesn't mail messages, it just collects them
        # in a list called ``messages``:
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