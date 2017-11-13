# -*- coding: utf-8 -*-

from five import grok

from plone import api

from Products.CMFCore.interfaces import ISiteRoot

grok.templatedir('templates')


class InserirFaqView(grok.View):
    """ View para adicionar várias mensagens ao Fale Conosco
    """

    grok.name('inserir-faq')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def textos(self):
        portal = api.portal.get()
        textos = getattr(portal, 'faq').objectValues()
        result = []
        for texto in textos:

            try:
                texto_prontos = texto.text.output
            except AttributeError:
                texto_prontos = ''

            result.append({
                'titulo':texto.title,
                'texto':texto_prontos
            })
        return result