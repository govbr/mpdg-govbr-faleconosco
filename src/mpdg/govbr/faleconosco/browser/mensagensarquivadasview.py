# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plone import api
from DateTime import DateTime

grok.templatedir('templates')

class MensagensArquivadasView(grok.View):
    """ View para administração das mensagens arquivadas"""

    grok.name('mensagens-arquivadas-admin')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        return super(MensagensArquivadasView, self).update()

    def mensagens_arquivadas(self):

        catalog = api.portal.get_tool('portal_catalog')
        brain   = catalog.searchResults(
            portal_type  = 'FaleConosco', # Pegar pelo Objeto Arquivado = True 
            arquivado    = True,
            sort_on      = 'modified'
        )
      

        mensagens = []
        for item in brain:
            obj = item.getObject()
            pathPhisical = obj.getPhysicalPath() 

            listarHistorico = catalog.searchResults(
                portal_type = 'Historico',
                path        = '/'.join(pathPhisical),
                sort_limit  = 1,
                sort_on     = 'created',
                sort_order  = "reverse"
                )[:1]

            nome = ''
            obs  = ''
            if listarHistorico: 
                objHistorico = listarHistorico[0].getObject()
                nome         = objHistorico.getNome()
                obs          = objHistorico.getObservacao()

            mensagens.append(
              {
                  'UID'  : obj.UID,                  
                  'assunto': obj.getAssunto(),
                  'nome': nome,
                  'observacao': obs
              }              
            )

        return mensagens










