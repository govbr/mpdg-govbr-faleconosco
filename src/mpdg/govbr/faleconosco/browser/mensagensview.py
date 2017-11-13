# -*- coding: utf-8 -*-

from five import grok
from plone import api
from Acquisition import aq_parent

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from mpdg.govbr.faleconosco.browser.utilities import get_wf_history

grok.templatedir('templates')


class MensagensView(grok.View):
    """ View para administracao do Fale Conosco
    """

    grok.name('mensagens')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self, **kwargs):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)

    def get_mensagens(self, uid):
        # metodo para pegar as mensagens do fale conosco
        ucatalog = getToolByName(self.context, 'uid_catalog')
        wtool = getToolByName(self.context, 'portal_workflow')
        busca = ucatalog(UID=uid)
        mensagens = []
        if busca:
            obj = busca[0].getObject()
            mensagens.append({
                'uid': uid,
                'mensagem': obj.getMensagem(),
                'estado': wtool.getInfoFor(obj, 'review_state'),
                'responsavel': obj.getResponsavel(),
                'assunto': obj.getAssunto(),
                'email': obj.getEmail(),
                'nome': obj.getNome(),
                'pai': uid,
                'data': obj.created().strftime('%d/%m/%Y')
            })

            catalog = api.portal.get_tool('portal_catalog')
            objetos = catalog.searchResults(
                portal_type='Mensagem',
                path='/'.join(obj.getPhysicalPath()),
                sort_on='created'
            )
            count = 0

            for objeto in objetos:
                item = objeto.getObject()

                mensagem = {}

                wf_history = wtool.getHistoryOf('fale_conosco_workflow', item)
                index = 1 if len(wf_history) > 1 else 0
                estado = wf_history[index]['review_state']

                mensagem['uid'] = item.UID()
                mensagem['mensagem'] = item.getMensagem()
                mensagem['estado'] = estado
                mensagem['responsavel'] = obj.getResponsavel()
                mensagem['assunto'] = obj.getAssunto()
                mensagem['email'] = obj.getEmail()
                mensagem['data'] = wf_history[index]['time'].strftime('%d/%m/%Y')
                mensagem['usuario'] = get_wf_history(objetos, item, count)
                mensagem['nome'] = obj.getNome()
                if obj.portal_type == 'FaleConosco':
                    mensagem['pai'] = obj.UID()
                if obj.portal_type == 'Mensagem':
                    mensagem['pai'] = aq_parent(obj).UID()
                if not mensagem['data']:
                    mensagem['data'] = obj.created().strftime('%d/%m/%Y')
                mensagens.append(mensagem)
                count += 1
        return mensagens
