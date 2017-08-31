# -*- coding: utf-8 -*-

from five import grok
from plone import api
from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.interfaces import ISiteRoot
from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired

grok.templatedir('templates')


class FaleCategorizar(FaleConoscoAdminRequired, grok.View):
    """ View que salvar as categorias..."""

    grok.name('fale-categorizar')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self):
        self.fale_uid = self.request.form['fale_uid']
        categorias = self.request.form['tags']
        self.categorias = categorias.split(',') 
        return self.buscar()

    def buscar(self):
        catalog = api.portal.get_tool('portal_catalog')
        # 1. pegar o objeto do fale conosco através do fale_uid
        buscar = catalog.searchResults(
            portal_type = 'FaleConosco',
            UID =  self.fale_uid
        )
        if buscar:
            # pegar o primeiro elemento da lista
            # chamar o getObject e atribuir em uma variavel

            item = buscar[0].getObject()
            item.setSubject(self.categorias)
            item.reindexObject()

            self.message('Categorização salva com sucesso!')
        else:
            self.message('Não foi encotrado a mensagem com esse UID ')

        return self.request.response.redirect('fale-conosco-admin')

    def message(self, mensagem):

        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return

            # 2. a partir desse objeto, definir as categorias recebidas na variavel 'categorias'
            # setSubject(self.categorias) <- no objeto que a gente pegou acima

            # 3. Informar uma mensagem dizendo ao usuario que as categorias foram atualizadas

            # 4. redirecionar o usuario para o painel de admin do fale conosco
