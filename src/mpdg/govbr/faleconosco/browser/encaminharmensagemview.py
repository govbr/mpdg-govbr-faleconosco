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
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IContextSourceBinder
from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired
from plone.i18n.normalizer import idnormalizer
from datetime import datetime
from mpdg.govbr.faleconosco.browser.utilities import FluxoMensagensView



grok.templatedir('templates')

def make_terms(items):
    """Create zope.schema terms for vocabularies from tuples"""

    terms = [
        SimpleTerm(value=item[0], token=item[0], title=item[1])
        for item in items
    ]

    return terms

@grok.provider(IContextSourceBinder)
def get_users(context):

    group_users = api.user.get_users(groupname='adm-fale-conosco')
    results     = []

    for user in group_users:

        results.append(
            (user.getProperty('id'), user.getProperty('fullname'))
        )

    user_vocab = schema.vocabulary.SimpleVocabulary(make_terms(results))
    return user_vocab


class IEncaminharMensagemForm(form.Schema):

    directives.mode(uids="hidden")
    uids = schema.TextLine(
        title=u"UIDS",
        required=True
    )

    usuario = schema.Choice(
        title=u'Encaminhar para',
        description=u'Escolha o usuario que você deseja encaminhar essa mensagem',
        required=True,
        source=get_users
    )

    directives.widget(mensagem='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    mensagem = schema.Text(
        title=u'Mensagem',
        required=True
    )


@form.default_value(field=IEncaminharMensagemForm['uids'])
def default_uids(data):
    return data.request.get('uids')


class EncaminharMensagemView(FaleConoscoAdminRequired, FluxoMensagensView, form.SchemaForm):
    """ View para adicionar várias mensagens ao Fale Conosco
    """
    # Nome da rota
    grok.name('encaminhar-mensagem')
    grok.require('zope2.View')
    # Quem pode acessar
    grok.context(ISiteRoot)

    schema        = IEncaminharMensagemForm
    ignoreContext = True
    label         = u"Encaminhar Mensagem"

    def _back_to_admin(self, message=None):
        portal_url = api.portal.get().absolute_url()
        fale_conosco = '{0}/@@fale-conosco-admin/'.format(portal_url)

        if message:

            messages = IStatusMessage(self.request)
            messages.add(message, type='info')

        return self.request.response.redirect(fale_conosco)


    def update(self):

        self.uids = self.request.form.get('form.widgets.uids') or self.request.form.get('uids')

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
            return super(EncaminharMensagemView, self).update()

        else:

            return self._back_to_admin(u'Vocẽ não pode acessar dessa forma!')

    # Cria um botão no formulario
    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):

        data, errors = self.extractData()
        # import pdb; pdb.set_trace()

        if errors:

            self.status = self.formErrorsMessage
            return

        responsavel = data['usuario']
        mensagem    = data['mensagem']
        vocab       = get_users(self.context)
        catalog     = api.portal.get_tool(name='portal_catalog')
        uids        = self.uids.split(',')
        brain       = catalog.searchResults(UID=uids)

        for item in brain:
            obj      = item.getObject()
            old_resp = obj.getResponsavel()
            obj.setResponsavel(responsavel)
            obj.reindexObject()

            nome    = vocab.getTerm(responsavel).title
            assunto =  obj.getAssunto()
            email   = obj.getEmail()

            id = idnormalizer.normalize(nome) + \
                '-' + str(datetime.now().microsecond)
            pt        = api.portal.get_tool(name='portal_types')
            type_info = pt.getTypeInfo('Mensagem')
            child     = type_info._constructInstance(obj, id)
            child.setTitle(nome)
            child.setNome(responsavel)
            child.setEmail(email)
            child.setAssunto(assunto)
            child.setMensagem(mensagem)
            child.setResponsavel(old_resp)
            child.reindexObject()

            api.content.transition(obj=obj, transition='encaminhar')
            api.content.transition(obj=child, transition='encaminhar')

        return self._back_to_admin(u'Mensagem(s) Encaminhada(s)!')

    @button.buttonAndHandler(u'Descartar')
    def handleCancel(self, action):
        return self._back_to_admin(u'Mensagem descartada')
