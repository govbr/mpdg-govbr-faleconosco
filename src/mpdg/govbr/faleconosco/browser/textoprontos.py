# -*- coding: utf-8 -*-

from five import grok
from plone import api

from Products.CMFCore.interfaces import ISiteRoot

grok.templatedir('templates')


class TextosProntosView(grok.View):
    """ View para adicionar vários textos prontos ao Fale Conosco
    """

    grok.name('textos-prontos')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def textos(self):
        portal = api.portal.get()
        textos = getattr(portal, 'textos-prontos').objectValues()  # [1, 2, 3, 4, 5]
        result = []
        for texto in textos:

            try:
                texto_prontos = texto.text.output
            except AttributeError:
                texto_prontos = ''

            result.append({
                'titulo' : texto.title, 
                'texto'  : texto_prontos
             })
        return result
