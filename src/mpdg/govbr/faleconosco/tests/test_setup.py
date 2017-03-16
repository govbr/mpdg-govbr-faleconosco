# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from mpdg.govbr.faleconosco.testing import MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that mpdg.govbr.faleconosco is properly installed."""

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mpdg.govbr.faleconosco is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'mpdg.govbr.faleconosco'))

    def test_browserlayer(self):
        """Test that IMpdgGovbrFaleconoscoLayer is registered."""
        from mpdg.govbr.faleconosco.interfaces import (
            IMpdgGovbrFaleconoscoLayer)
        from plone.browserlayer import utils
        self.assertIn(IMpdgGovbrFaleconoscoLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['mpdg.govbr.faleconosco'])

    def test_product_uninstalled(self):
        """Test if mpdg.govbr.faleconosco is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'mpdg.govbr.faleconosco'))

    def test_browserlayer_removed(self):
        """Test that IMpdgGovbrFaleconoscoLayer is removed."""
        from mpdg.govbr.faleconosco.interfaces import \
            IMpdgGovbrFaleconoscoLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMpdgGovbrFaleconoscoLayer, utils.registered_layers())
