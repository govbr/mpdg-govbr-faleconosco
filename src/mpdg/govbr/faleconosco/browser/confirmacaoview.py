# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from plone import api
from mpdg.govbr.faleconosco.browser.utilities import transform_message, get_fale_config

grok.templatedir('templates')


class ConfirmacaoView(grok.View):
    """ View para a visualizacao da confirmacao do envio do fale conosco
    """

    grok.name('confirmacao')
    grok.require('zope2.View')
    grok.context(Interface)

    def get_portal_url(self):
        return api.portal.get().absolute_url()

    def get_message(self):
        nome = self.request.form['nome']
        email = self.request.form['email']
        mensagem = self.request.form['mensagem']
        text = get_fale_config('enviar_email_form')
        assunto= self.request.form['assunto']
        msg = transform_message(text, nome, email, mensagem, assunto)
        return {
            'msg': msg,
            'email': email
        }
