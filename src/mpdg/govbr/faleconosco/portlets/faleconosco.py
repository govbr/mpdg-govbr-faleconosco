# -*- coding: utf-8 -*-

import pandas as pd
from pandas.tseries.offsets import BDay
from zope.interface import implements
from Acquisition import aq_inner
from DateTime import DateTime
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from mpdg.govbr.faleconosco import MessageFactory as _
from mpdg.govbr.faleconosco.config import DIAS_PRAZO, DIAS_ATRASO, DIAS_ALERTA
from mpdg.govbr.faleconosco.interfaces import IFaleConosco


class IFaleConoscoPortlet(IPortletDataProvider):
    """ portlet do fale conosco (admin)
    """


class Assignment(base.Assignment):
    """ Portlet assignment
    """

    implements(IFaleConoscoPortlet)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Fale Conosco"


class Renderer(base.Renderer):
    """ Portlet renderer.
    """

    render = ViewPageTemplateFile('templates/faleconosco.pt')

    def __init__(self, *args):

        base.Renderer.__init__(self, *args)
        context      = aq_inner(self.context)
        self.catalog = getToolByName(context, 'portal_catalog')

    def no_prazo(self):

        # metodo que busca as mensagens no prazo
        hoje  = pd.datetime.today()
        prazo = DateTime(hoje - BDay(DIAS_PRAZO)).asdatetime().date()
        
        busca = self.catalog(
            object_provides = IFaleConosco.__identifier__,
            created         = {'query': (DateTime(hoje), prazo), 'range': 'min:max'},
            review_state    = ['novo', 'encaminhado', 'resgatado']
        )
        return len(busca)

    def alerta(self):

        # metodo que busca as mensagens em alerta
        hoje   = pd.datetime.today()
        prazo  = DateTime(hoje - BDay(DIAS_PRAZO)).asdatetime().date()
        alerta = DateTime(hoje - BDay(DIAS_ALERTA)).asdatetime().date()

        busca  = self.catalog(
            object_provides = IFaleConosco.__identifier__,
            created         = {'query': (prazo, alerta), 'range': 'min:max'},
            review_state    = ['novo', 'encaminhado', 'resgatado']
        )

        return len(busca)

    def atraso(self):
        # metodo que busca as mensagens em atraso
        hoje   = pd.datetime.today()
        alerta = DateTime(hoje - BDay(DIAS_ALERTA)).asdatetime().date()
        atraso = DateTime(hoje - BDay(DIAS_ATRASO)).asdatetime().date()
        busca  = self.catalog(
            object_provides = IFaleConosco.__identifier__,
            created         = {'query': (alerta, atraso), 'range': 'min:max'},
            review_state    = ['novo', 'encaminhado', 'resgatado']
        )

        return len(busca)


class AddForm(base.NullAddForm):

    form_fields = form.Fields(IFaleConoscoPortlet)
    label       = _(u"Adicionar o portlet do Fale Conosco")
    description = _(u"")

    def create(self):

        return Assignment()
