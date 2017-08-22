# -*- coding: utf-8 -*-
from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.directives import form
from plone.supermodel import model
from zope import schema
from z3c.form import button
from plone.autoform import directives

from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired, FluxoMensagensView


grok.templatedir('templates')


class IResponderSelecionadosForm(form.Schema):
    directives.mode(uids='hidden')
    uids = schema.TextLine(title=u"UIDS", required=True)

    directives.widget(mensagem='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    mensagem = schema.Text(
        title=u'Mensagem',
        required=True
    )

    directives.mode(estado='hidden')
    estado = schema.TextLine(
        title=u"Workflow",
        required=True,
        default=u'responder'
    )

@form.default_value(field=IResponderSelecionadosForm['uids'])
def default_uids(data):
    return data.request.get('uids')


class ResponderSelecionadosView(FaleConoscoAdminRequired, FluxoMensagensView, form.SchemaForm):
    """ View para adicionar várias mensagens ao Fale Conosco
    """
    grok.name('responder-selecionados')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = IResponderSelecionadosForm
    ignoreContext = True

    label = u"Responder Selecionados"

    @property
    def action(self):
        portal_url = api.portal.get().absolute_url()
        target = '{0}/@@add-mensagem'.format(portal_url)
        return target

    def updateActions(self):
        self.request.set('disable_border', True)
        super(ResponderSelecionadosView, self).updateActions()

    @button.buttonAndHandler(u'Descartar')
    def handleCancel(self, action):
        return self._back_to_admin(u'Mensagem descartada')

    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

    def _back_to_admin(self, message=None):
        portal_url = api.portal.get().absolute_url()
        fale_conosco = '{0}/@@fale-conosco-admin/'.format(portal_url)

        if message:
            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        return self.request.response.redirect(fale_conosco)

    def update(self):
        self.uids = self.request.get('uids')
        if not self.uids:
            return self._back_to_admin(u'Você não pode acessar essa página diretamente')

        brain = self.get_messages_uids(self.uids.split(','))
        if not brain:
            return self._back_to_admin(u'Nenhuma mensagem com esse UID foi encontrada.')

        self.messages = self.get_nomes(brain)
        return super(ResponderSelecionadosView, self).update()

    def get_messages_uids(self, uids):
        catalog = api.portal.get_tool(name='portal_catalog')
        brain = catalog.searchResults(
            UID=uids
        )
        return brain

    def get_nomes(self, brain):
        result = []
        for item in brain:
            obj = item.getObject()
            result.append(obj.nome)
        return ', '.join(result)
