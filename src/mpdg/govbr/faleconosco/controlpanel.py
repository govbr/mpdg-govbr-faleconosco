    # -*- coding: utf-8 -*-

from zope import schema
from five import grok
from Products.CMFCore.interfaces import ISiteRoot

from plone.z3cform import layout
from plone.directives import form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper


class IFaleSettings(form.Schema):
    """
    """

    enviar_email = schema.Bool(title=u"Enviar e-mail",
                               description=u"Selecione caso queira que o sistema envie um e-mail de confirmação")

    admfale = schema.TextLine(
        title=u'Usuário administrador do Fale Consoco',
        description=u'Informe o ID do usuário administrador do Fale Conosco',
        required=True,
        default=u'idg',
    )


class FaleSettingsEditForm(RegistryEditForm):
    """
    """
    schema = IFaleSettings
    label = u"mpdg.govbr: Fale Conosco"


class SettingsView(grok.View):
    """
    """
    grok.name("fale-settings")
    grok.context(ISiteRoot)

    def render(self):
        view_factor = layout.wrap_form(FaleSettingsEditForm, ControlPanelFormWrapper)
        view = view_factor(self.context, self.request)
        return view()
