    # -*- coding: utf-8 -*-

from zope import schema
from five import grok
from Products.CMFCore.interfaces import ISiteRoot

from plone.z3cform import layout
from plone.directives import form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from mpdg.govbr.faleconosco.config import EMAIL_FALE, EMAIL_FALE_ASSINATURA
from plone.autoform import directives




class IFaleSettings(form.Schema):
    """
    """

    enviar_email = schema.Bool(title=u"Enviar e-mail",
                               description=u"Selecione caso queira que o sistema envie um e-mail de confirmação")

    admfale = schema.TextLine(
        title=u'Usuário administrador do Fale Consoco',
        description=u'Informe o ID do usuário administrador do Fale Conosco',
        required=True,
        default=u'catia.parreira'
    )


    directives.widget(enviar_email_form='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    enviar_email_form = schema.Text(
        title=u'Mensagem Confirmação de email ',
        description=u"""Informe a mensagem que o usuário irá receber após enviar uma mensagem pelo Fale Conosco.
        Variáveis: [nome],[email],[mensagem],[assunto].""",
        required=True,
        default=EMAIL_FALE
    )

    directives.widget(enviar_email_assinatura='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    enviar_email_assinatura =schema.Text(
        title=u'Mensagem de Assinatura',
        description=u'Informe a assinatura de email. Será exibida no final da mensagem',
        required=True,
        default=EMAIL_FALE_ASSINATURA

     )


class FaleSettingsEditForm(RegistryEditForm):
    """
    """
    schema = IFaleSettings
    label = u"Configurações do Fale Conosco "


class SettingsView(grok.View):
    """
    """
    grok.name("fale-settings")
    grok.context(ISiteRoot)
    grok.require('cmf.ManagePortal')

    def render(self):
        view_factor = layout.wrap_form(FaleSettingsEditForm, ControlPanelFormWrapper)
        view = view_factor(self.context, self.request)
        return view()
