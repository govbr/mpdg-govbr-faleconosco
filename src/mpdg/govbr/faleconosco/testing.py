# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2


class MpdgGovbrFaleconoscoLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import mpdg.govbr.faleconosco
        self.loadZCML(name='testing.zcml', package=mpdg.govbr.faleconosco)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'mpdg.govbr.faleconosco:testing')


MPDG_GOVBR_FALECONOSCO_FIXTURE = MpdgGovbrFaleconoscoLayer()


MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MPDG_GOVBR_FALECONOSCO_FIXTURE,),
    name='MpdgGovbrFaleconoscoLayer:IntegrationTesting'
)
