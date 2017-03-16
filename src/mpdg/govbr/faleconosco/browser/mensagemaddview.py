# -*- coding: utf-8 -*-

from five import grok
from datetime import datetime
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone.i18n.normalizer import idnormalizer
from plone import api
from mpdg.govbr.faleconosco.mailer import simple_send_mail
from mpdg.govbr.faleconosco.utils import prepare_email_message

grok.templatedir('templates')

class MensagemAddView(grok.View):
    """ View para adicionar mensagem ao Fale Conosco """

    grok.name('add-mensagem')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self, **kwargs):

        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)

    def _get_form_vars(self, form):

        uids     = form.get('uids', None) or form.get('form.widgets.uids', None)
        estado   = form.get('estado', None) or form.get('form.widgets.estado', None)
        mensagem = form.get('mensagem', None) or form.get('form.widgets.mensagem', None)

        return {
            'uids': uids,
            'mensagem': mensagem,
            'estado': estado,
        }

    def render(self, **kwargs):
        """
        Este metodo tem as funcionalidades de 
        responder, encaminhar e resgatar.
        Só quem pode responder de fato é o Adminitrador do fale conosco,
        os demais usuários pode apenas encaminhar a resposta para o Administrador,
        para que ele encaminhe de volta para o usuário final (remetente).
        O encaminhamento é feito sempre pelo usuário logado, seja ele Administrador
        ou Responsável pela mensagem.
        O responsável pela mensagem pode encaminhar para outros usuários do Fale Conosco
        Podendo também resgatar a mensagem, caso tenha cometido algum engano.
        """

        ucatalog       = getToolByName(self.context, 'uid_catalog')
        wtool          = getToolByName(self.context, 'portal_workflow')
        mtool          = getToolByName(self.context, 'portal_membership')
        pt             = getToolByName(self.context, 'portal_types')
        request        = self.context.REQUEST
        status_message = IStatusMessage(request)
        form           = self._get_form_vars(request.form)
        uids           = form.get('uids', None)
        acao           = form.get('estado', None)
        mensagem       = form.get('mensagem', None)
        userlogged     = api.user.get_current().id


        if uids:
            # uids dos objetos FaleConosco (pai)
            for uid in uids.split(','):

                fale = ucatalog(UID=uid)[0]
                obj  = fale.getObject()
                # cria a mensagem
                # TODO: criar metadados no catalog
                nome        = obj.getNome()
                assunto     = self.get_assunto(fale)
                email       = obj.getEmail()
                responsavel = obj.getResponsavel()

                id = idnormalizer.normalize(nome) + \
                    '-' + str(datetime.now().microsecond)

                type_info = pt.getTypeInfo('Mensagem')
                item      = type_info._constructInstance(obj, id)
                item.setTitle(nome)
                item.setNome(nome)
                item.setEmail(email)
                item.setAssunto(assunto)
                item.setMensagem(mensagem)
                item.setResponsavel(userlogged)
                item.reindexObject()
                # apos criar a mensagem altera o workflow
                # da mensagem e do objeto pai
                wtool.doActionFor(obj, acao)
                wtool.doActionFor(item, acao)

                assunto = 'Fale conosco: resposta'
                endereco = email
                mensagem_mail = prepare_email_message(mensagem, html=True)
                simple_send_mail(mensagem_mail, endereco, assunto)

            status_message.add(u"Mensagens respondidas com sucesso!",
                               type=u"info")

            contextURL = self.context.absolute_url() + '/@@fale-conosco-admin'
            return self.request.response.redirect(contextURL)

        else:

            uid = request.form.get('pai', None)
            if not uid:
                uid = request.form.get('msg')

            nome        = request.form.get('nome', None)
            email       = request.form.get('email', None)
            assunto     = request.form.get('assunto', None)
            userid      = request.form.get('userid', None)
            responsavel = request.form.get('responsavel', None)
            id = idnormalizer.normalize(nome) + \
                '-' + str(datetime.now().microsecond)

            # pega o objeto pai
            # if uid:

            fale = ucatalog(UID=uid)[0].getObject()

            if acao == 'resgatar':
                member      = mtool.getAuthenticatedMember()
                responsavel = member.getId()
                email       = member.getProperty('email')
                assunto     = fale.getAssunto()
                fale.setResponsavel(userlogged)
                fale.reindexObject()

            # apos criar e alterar o estado do workflow,
            # seta o responsavel no fale
            if acao == 'encaminhar':
                
                userid      = request.form.get('userid', None)
                fale.setResponsavel(userid)
                fale.reindexObject()

            # cria a mensagem
            type_info = pt.getTypeInfo('Mensagem')
            item      = type_info._constructInstance(fale, id)
            item.setTitle(nome)
            item.setNome(userid)
            item.setEmail(email)
            item.setAssunto(assunto)
            item.setMensagem(mensagem)
            #seta no objeto filho o responsável pelo encaminhamento ou seja quem está logado.
            item.setResponsavel(userlogged) 
            item.reindexObject()

            # apos criar a mensagem altera o workflow da
            # mensagem e do objeto pai
            wtool.doActionFor(fale, acao)
            wtool.doActionFor(item, acao)

            assunto       = 'Fale conosco'
            endereco      = email
            mensagem_mail = prepare_email_message(mensagem, html=True)
            simple_send_mail(mensagem_mail, endereco, assunto)

            status_message.add(u"Alteração realizada com sucesso!", 
                               type=u"info")

            contextURL = self.context.absolute_url() + \
                '/@@fale-conosco-admin?msg=' + uid
            return self.request.response.redirect(contextURL)

    def get_assunto(self, conteudo):
        # metodo para buscar o titulo do assunto

        factory = getUtility(IVocabularyFactory, u'mpdg.govbr.faleconosco.Assuntos')
        vocab   = factory(self.context)
        termo   = conteudo.getObject().getAssunto()

        try:

            assunto = vocab.getTerm(termo)
            return assunto.title

        except LookupError:
            return ''

    def _back_to_admin(self):

        p_url  = api.portal.get().absolute_url()
        target = '{0}/@@fale-conosco-admin'.format(p_url)

        return self.request.response.redirect(target)

    def message(self, mensagem):

        messages = IStatusMessage(self.request)
        messages.add(mensagem, type='info')
        return
