# -*- coding: utf-8 -*-
from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form
from zope import schema
from z3c.form import button
from plone.autoform import directives

from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired
from DateTime.DateTime import DateTime
from datetime import datetime
from plone.i18n.normalizer import idnormalizer
from Products.CMFCore.utils import getToolByName
from mpdg.govbr.faleconosco.browser.utilities import FluxoMensagensView


grok.templatedir('templates')

#Criando a interface do formulário
class IFormArquivarMensagemView(form.Schema):
    # Criando os campos do formulário
    directives.mode(uids='hidden')
    uids       = schema.TextLine(title=u"UIDS", required=True)
    observacao = schema.Text(title=u"Motivo:", required=True)

# Renderizando o formulário
@form.default_value(field=IFormArquivarMensagemView['uids'])
def default_uids(data):
    return data.request.get('uids')

#Fim
#Criando a view do formulário
class FormArquivarMensagemView(FaleConoscoAdminRequired, FluxoMensagensView,form.SchemaForm):
    #Setando o nome da URL
    grok.name('justificar-arquivamento-de-mensagem')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = IFormArquivarMensagemView
    ignoreContext = True

    label = u"Arquivar Mensagem"

    def assunto(self):
        # fazer busca e retornar assunto da msg
        catalog = api.portal.get_tool(name='portal_catalog')
        brain   = catalog.searchResults(UID=self.uids)
        if brain:
            form     = brain[0].getObject()
            mensagem = form.getAssunto()
            return mensagem

    def update(self):
        # Captura o UID da mensagem.
        self.uids = self.request.form.get('form.widgets.uids') or self.request.form.get('uids')
        
        # Retira as opões de edição da página.(Barrinha verde)
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        # Checa se o UID foi setado
        if not self.uids:
            return self._back_to_admin(u'Você não pode acessar essa página diretamente')
        return super(FormArquivarMensagemView, self).update()

    def updateActions(self):
        self.request.set('disable_border',True)
        return super(FormArquivarMensagemView, self).updateActions()

    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):
        data, errors = self.extractData()
        # Método para pegar o portal_types, para realizar o armazenamento.
        pt = getToolByName(self.context, 'portal_types')

        if errors:
            self.status = self.formErrorsMessage

        msg        = data['observacao']
        nome       = api.user.get_current().id # Pega o id do usuário logado.
        catalog    = api.portal.get_tool(name='portal_catalog')
        brain      = catalog.searchResults(UID=self.uids)

        if brain:
            fale = brain[0].getObject()
            fale.setArquivado(True) # Verificar se este valor está sendo passado corretamente.

            # Cria o objeto historico dentro do tipo de conteudo FaleConosco
            id = idnormalizer.normalize(nome) + \
                    '-' + str(datetime.now().microsecond)

            type_info = pt.getTypeInfo('Historico')

            item = type_info._constructInstance(fale, id)
            item.setNome(nome)
            item.setEstado('arquivado')
            item.setObservacao(msg)
            item.reindexObject()

            import transaction; transaction.commit()
            # obj.reindexObject()
            catalog.reindexObject(fale)
            self.message('Mensagem arquivada com sucesso!')
            return self._back_to_admin()
        else:
            self.message('A mensagem não pode ser arquivada')
            return self._back_to_admin()

    def _back_to_admin(self, message=None):
        portal_url = api.portal.get().absolute_url()
        fale_conosco = '{0}/@@fale-conosco-admin/'.format(portal_url)

        if message:
            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        return self.request.response.redirect(fale_conosco)

    def message(self, mensagem):
        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return