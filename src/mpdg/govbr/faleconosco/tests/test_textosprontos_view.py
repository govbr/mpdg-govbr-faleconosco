#-*- coding: utf-8 -*-
import unittest
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedFile
from plone.testing.z2 import Browser


class TextosProntosViewTest(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING


    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_view_textosprontos(self):
        view = self.portal.restrictedTraverse('@@textos-prontos')
        self.assertTrue(view)
   
    
    # # Teste de Mensagem do TextosProntosViewTest
    # def test_mime_icon_odt_for_file_(self):
       
    #     self.browser.open(self.portal_url)
    #     self.browser.getLink('view').click()

    #     widget = 'form.widgets.title'
    #     self.browser.getControl(name=widget).value = 'My file'
    #     widget = 'form.widgets.description'
    #     self.browser.getControl(name=widget).value = 'This is my odt file.'
    #     file_path = os.path.join(os.path.dirname(__file__), 'file.odt')
    #     file_ctl = self.browser.getControl(name='form.widgets.file')
    #     file_ctl.add_file(io.FileIO(file_path),
    #                       'application/vnd.oasis.opendocument.text',
    #                       'file.odt')
    #     self.browser.getControl('Save').click()
    #     self.assertTrue(self.browser.url.endswith('file.odt/view'))
    #     self.assertTrue('application.png' in self.browser.contents)