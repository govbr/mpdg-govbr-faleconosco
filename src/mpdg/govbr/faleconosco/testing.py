# -*- coding: utf-8 -*-
# from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
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
        self.loadZCML(package=mpdg.govbr.faleconosco)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'mpdg.govbr.faleconosco:default')


MPDG_GOVBR_FALECONOSCO_FIXTURE = MpdgGovbrFaleconoscoLayer()


MPDG_GOVBR_FALECONOSCO_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MPDG_GOVBR_FALECONOSCO_FIXTURE,),
    name='MpdgGovbrFaleconoscoLayer:IntegrationTesting'
)


# MPDG_GOVBR_FALECONOSCO_FUNCTIONAL_TESTING = FunctionalTesting(
#     bases=(MPDG_GOVBR_FALECONOSCO_FIXTURE,),
#     name='MpdgGovbrFaleconoscoLayer:FunctionalTesting'
# )


# MPDG_GOVBR_FALECONOSCO_ACCEPTANCE_TESTING = FunctionalTesting(
#     bases=(
#         MPDG_GOVBR_FALECONOSCO_FIXTURE,
#         REMOTE_LIBRARY_BUNDLE_FIXTURE,
#         z2.ZSERVER_FIXTURE
#     ),
#     name='MpdgGovbrFaleconoscoLayer:AcceptanceTesting'
# )
