# -*- encoding: utf-8 -*-
from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form
from plone.supermodel import model
from zope import schema
from z3c.form import button
from plone.autoform import directives
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired
from plone.i18n.normalizer import idnormalizer
from datetime import datetime
from mpdg.govbr.faleconosco.browser.utilities import FluxoMensagensView

grok.templatedir('templates')

class IEncaminharAdminForm(form.Schema):
    directives.mode(uids="hidden")
    uids       = schema.TextLine(title=u"UIDS", required=True)
    mensagem   = schema.Text(title=u"Mensagem:", required=True)


@form.default_value(field=IEncaminharAdminForm['uids'])
def default_uids(data):
    return data.request.get('uids')


class EncaminharAdminView(FaleConoscoAdminRequired, FluxoMensagensView, form.SchemaForm):
    """ View para adicionar várias mensagens ao Fale Conosco
    """
    # Nome da rota
    grok.name('encaminhar-admin-view')
    grok.require('zope2.View')
    # Quem pode acessar
    grok.context(ISiteRoot)

    schema        = IEncaminharAdminForm
    ignoreContext = True
    label         = u"Encaminhar a mensagem para o administrador do Fale Conosco."

    def responsavel(self):

        # fazer busca e retornar assunto da msg
        catalog = api.portal.get_tool(name='portal_catalog')
        brain   = catalog.searchResults(UID=self.uids)

        if brain:

            form           = brain[0].getObject()
            oldresponsavel = form.getResponsavel()
            return oldresponsavel

    def _back_to_admin(self, message=None):

        portal_url   = api.portal.get().absolute_url()
        fale_conosco = '{0}/@@fale-conosco-admin/'.format(portal_url)

        if message:

            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        return self.request.response.redirect(fale_conosco)

    def get_adm_fale(self):
        # Pega o usuário administrador do fale conosco.

        registry = getUtility(IRegistry)
        adm_fale = registry.records['mpdg.govbr.faleconosco.controlpanel.IFaleSettings.admfale'].value
        return adm_fale


    def update(self):
        self.uids = self.request.form.get('form.widgets.uids') or self.request.form.get('uids')
         # Retira as opões de edição da página.(Barrinha verde)
        self.request.set('disable_border', True)


        if self.uids:

            uids    = self.uids.split(',')
            catalog = api.portal.get_tool(name='portal_catalog')

            search  = catalog.searchResults(
                UID = uids
            )

            lista = []

            for obj in search:

                title = obj.getObject().Title()

                if title:

                    lista.append(title)

                else:

                    title = obj.getObject().getAssunto()
                    lista.append(title)

            self.results = ', '.join(lista)
            return super(EncaminharAdminView, self).update()

        else:

            return self._back_to_admin(u'Vocẽ não pode acessar dessa forma!')

    # Cria um botão no formulario
    @button.buttonAndHandler(u'Enviar')

    def handleApply(self, action):

        data, errors = self.extractData()

        if errors:

            self.status = self.formErrorsMessage
            return

        responsavel = self.get_adm_fale()
        mensagem    = data['mensagem']
        catalog     = api.portal.get_tool(name='portal_catalog')
        uids        = self.uids.split(',')
        brain       = catalog.searchResults(UID=uids)

        for item in brain:

            obj      = item.getObject()
            old_resp = self.responsavel()
            obj.setResponsavel(responsavel)
            obj.reindexObject()

            nome = responsavel
            id   = idnormalizer.normalize(nome) + \
                '-' + str(datetime.now().microsecond)
            pt        = api.portal.get_tool(name='portal_types')
            type_info = pt.getTypeInfo('Mensagem')
            child     = type_info._constructInstance(obj, id)
            child.setTitle(nome)
            child.setNome(responsavel)
            child.setMensagem(mensagem)
            child.setResponsavel(old_resp)
            child.reindexObject()

            api.content.transition(obj = obj,  transition = 'encaminhar')
            api.content.transition(obj = child,transition = 'encaminhar')

        return self._back_to_admin(u'Mensagem encaminhada!')

    @button.buttonAndHandler(u'Descartar')

    def handleCancel(self, action):

        return self._back_to_admin(u'Mensagem descartada')

    def assunto(self):
        # fazer busca e retornar assunto da msg

        catalog = api.portal.get_tool(name='portal_catalog')
        brain   = catalog.searchResults(UID=self.uids)

        if brain:
            form     = brain[0].getObject()
            mensagem = form.getAssunto()
            return mensagem
