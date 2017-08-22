# -*- coding: utf-8 -*-
from plone import api
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from AccessControl import Unauthorized


def get_wf_history(brains, item, count):
    """Retorna histórico de workflow das mensagens do fale conosco
    :param brains: Resultado da busca no portal_catalog do objeto Mensagem
    :param item: Mensagem em específico que queremos obter o histórico de workflow (objeto obtido c/ getObject())
    :param count: numero de cada iteração dentro da lista de objetos (brains)
    :return: Responsável da mensagem ou histórico de encaminhamentos/resgate das mensagens
    """
    wtool = api.portal.get_tool('portal_workflow')
    wf_history = wtool.getHistoryOf('fale_conosco_workflow', item)
    index = 1 if len(wf_history) > 1 else 0
    estado = wf_history[index]['review_state']

    if estado == 'encaminhado':
        try:
            # De: 'Responsável Atual' para 'Próximo Responsável'
            msg = brains[count + 1].getObject()
            mensagem = '<span class="negrito">de</span> %s <span class="negrito">Para</span> %s' % \
                                  (item.getResponsavel(), msg.getResponsavel())
        except IndexError:
            # Caso não identifique o Próximo Responsável, o except faz o tratamento para pegar
            # o nome do último usuário
            msg = brains[-1:][0].getObject()
            mensagem = '<span class="negrito">de</span> %s <span class="negrito">Para</span> %s' % \
                                  (item.getResponsavel(), msg.getNome())
    elif estado == 'resgatado':
        try:
            msg = brains[count - 1].getObject()
            mensagem = '<span class="negrito">de</span> %s <span class="negrito">Para</span> %s' % \
                                  (msg.getResponsavel(), item.getResponsavel(),)
        except IndexError:
            mensagem = item.getResponsavel()
    else:
        mensagem = item.getResponsavel()

    return mensagem


class FluxoMensagensView(object):
    def get_messages(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        uids = self.uids.split(',')
        search = catalog.searchResults(
            UID=uids
        )
        lista = []
        for obj in search:
            fale = obj.getObject()
            result = {
                'titulo': self._get_title(fale),
                'mensagens': self._get_fluxo_mensagens(fale)
            }
            lista.append(result)

        return lista

    def _get_fluxo_mensagens(self, fale):
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(
            portal_type='Mensagem',
            path='/'.join(fale.getPhysicalPath()),
            sort_on='created'
        )
        messages = [{
            'titulo': fale.getAssunto(),
            'msg': fale.getMensagem()
        }]
        count = 0
        for brain in brains:
            obj = brain.getObject()
            titulo = get_wf_history(brains, obj, count)
            messages.append(
                {
                    'titulo': titulo,
                    'msg': obj.getMensagem()
                }
            )
            count += 1
        return messages

    def _get_title(self, obj):
        """obtem o titulo da mensagem"""
        title = obj.getAssunto()
        if title:
            result = title
        else:
            result = obj.Title()
        return result

    def mensagem_title(self):
        mensagens = self.get_messages()
        results = []
        for item in mensagens:
            results.append(item['titulo'])
        return ', '.join(results)


class FaleConoscoAdminRequired(object):
    def update(self):
        if not api.user.is_anonymous():
            user_id = api.user.get_current().id
            users_fale = api.user.get_users(groupname='adm-fale-conosco')

            registry = getUtility(IRegistry)
            adm_fale = registry.records['mpdg.govbr.faleconosco.controlpanel.IFaleSettings.admfale'].value

            if user_id in [user.id for user in users_fale] \
                    or 'Manager' in api.user.get(user_id).getRoles() \
                    or user_id == adm_fale:
                pass
            else:
                raise Unauthorized("You need permission to access this page")
        else:
            raise Unauthorized("You need permission to access this page")
        return super(FaleConoscoAdminRequired, self).update()
