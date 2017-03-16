# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from plone import api

grok.templatedir('templates')


class ConfirmacaoView(grok.View):
    """ View para a visualizacao da confirmacao do envio do fale conosco
    """

    grok.name('confirmacao')
    grok.require('zope2.View')
    grok.context(Interface)

    def get_portal_url(self):
        return api.portal.get().absolute_url()


    def update(self):
        self.dados = self.get_dados()
        return super(ConfirmacaoView, self).update()
     
    def get_dados(self):
        result = {
            'nome': self.request.form['nome'],
            'titulo': self.request.form['assunto'],
            'email': self.request.form['email'],
            'mensagem': self.request.form ['mensagem']
        }
        if result:
            return result
        else:
            print "Não foi possível mostrar os resultados."