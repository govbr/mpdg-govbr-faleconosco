# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired
from plone import api
from Products.statusmessages.interfaces import IStatusMessage

grok.templatedir('templates')


class ArquivarMensagemView(FaleConoscoAdminRequired, grok.View):
    grok.name('arquivar-mensagem')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self):

        uids = self.request.form.get('uids')

        if not uids:

            self.message(u'Você não pode acessar essa página diretamente')
            return self._back_to_admin()

        catalog = api.portal.get_tool(name='portal_catalog')
        brain   = catalog.searchResults(UID=uids)

        if brain:

            obj = brain[0].getObject()

            if api.content.get_state(obj) == 'respondido':
                api.content.transition(obj=obj, transition='arquivar')

                self.message('Mensagem arquivada com sucesso!')
                return self._back_to_admin()

            else:

                self.message('A mensagem não pode ser arquivada')
                return self._back_to_admin()
        else:

            self.message('Não foi encontrada nenhuma mensagem com esse UID')
            return self._back_to_admin()

        return super(ArquivarMensagemView, self).update()

    def _back_to_admin(self):

        p_url  = api.portal.get().absolute_url()
        target = '{0}/@@fale-conosco-admin'.format(p_url)

        return self.request.response.redirect(target)

    def message(self, mensagem):

        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return
