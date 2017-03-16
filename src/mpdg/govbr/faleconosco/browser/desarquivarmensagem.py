# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired
from plone import api
from Products.statusmessages.interfaces import IStatusMessage
from mpdg.govbr.faleconosco.browser.utilities import FluxoMensagensView

grok.templatedir('templates')


class DesarquivarMensagemView(FaleConoscoAdminRequired, FluxoMensagensView ,grok.View):
    """docstring for ClassName"""
    grok.name('desarquivar-mensagem')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def assunto(self):
        # fazer busca e retornar assunto da msg
        catalog = api.portal.get_tool(name='portal_catalog')
        brain   = catalog.searchResults(UID=self.uids)
        if brain:
            form     = brain[0].getObject()
            mensagem = form.getAssunto()
            return mensagem

    def update(self): 
        uids = self.request.form.get('uids')
        if not uids:
            self.message('Você não pode acessar a página diretamente')
            return self._back_to_admin()

        catalog = api.portal.get_tool(name='portal_catalog')
        brain   = catalog.searchResults(UID=uids)

        if brain:

            obj = brain[0].getObject()
            obj.setArquivado(False) # Verificar se este valor está sendo passado corretamente.
            import transaction; transaction.commit()
            # obj.reindexObject()
            catalog.reindexObject(obj)
            self.message('Mensagem desarquivada com sucesso')
            return self._back_to_admin()            

        else:

            self.message('Mensagem não pode ser encontrada')
            return self._back_to_admin()


    def _back_to_admin(self):
        p_url = api.portal.get().absolute_url()
        target = '{0}/@@mensagens-arquivadas-admin'.format(p_url)
        return self.request.response.redirect(target)

    def message(self, mensagem):
        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return