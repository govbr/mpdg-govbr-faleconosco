# -*- coding: utf-8 -*-
import hashlib
import random
import urllib
from five import grok
from zope.interface import Interface
from plone import api
from plone.supermodel import model
from plone.directives import form
from plone.registry.interfaces import IRegistry
from zope import schema
from zope.schema.interfaces import RequiredMissing, TooLong
from zope.annotation import IAnnotations
from zope.component import getUtility
from z3c.form import button
from Products.CMFCore.utils import getToolByName
from mpdg.govbr.faleconosco.config import KEY_CONFIRMA, EMAIL_FALE
from mpdg.govbr.faleconosco.mailer import simple_send_mail
from mpdg.govbr.faleconosco.utils import prepare_email_message

grok.templatedir('templates')


class IFaleConoscoForm(model.Schema):
    nome     = schema.TextLine(title=u"Nome", required=True , max_length=50)
    email    = schema.TextLine(title=u"E-mail", required=True)
    assunto  = schema.TextLine(title=u"Título", required=True , max_length=100)
    mensagem = schema.Text(title=u"Mensagem", required=True)


@form.error_message(field=IFaleConoscoForm['nome'], error=RequiredMissing)
def nome_error_message(value):
    return u"Informe o seu nome."

@form.error_message(field=IFaleConoscoForm['nome'], error=TooLong)
def caracteres_max_nome(value):
    return u"Quantidade máxima de 50 caracteres permitidos "


@form.error_message(field=IFaleConoscoForm['assunto'], error=TooLong)
def caracteres_max_titulo(value):
    return u"Quantidade máxima de 100 caracteres permitidos "


class FaleConoscoForm(form.SchemaForm):
    """ Formulario do fale conosco
    """
    grok.name('fale-conosco')
    grok.require('zope2.View')
    grok.context(Interface)

    schema = IFaleConoscoForm
    ignoreContext = True

    label = u"Fale conosco"
#    description = u"Um simples fale conosco"

    def updateActions(self):
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        super(FaleConoscoForm, self).updateActions()

    # def action(self):
    #     return api.portal.get().absolute_url() + "/@@confirmacao" 

    def faq(self):
        portal = api.portal.get()
        catalog = getToolByName(portal, 'portal_catalog')
        faq_list = []
        faq = getattr(portal, 'faq', None)
        if faq:
            brain = catalog(
                portal_type='Document', 
                path='/'.join(faq.getPhysicalPath()),
                review_state='published'
            )

            for item in brain:
                faq_dic = {
                    'url': item.getURL(),
                    'titulo': item.Title
                }
                faq_list.append(faq_dic)

        return faq_list

    
    @button.buttonAndHandler(u'Enviar')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return


        nome     = data['nome']
        email    = data['email']
        assunto  = data['assunto']
        mensagem = data['mensagem']

        registry    = getUtility(IRegistry)
        adm_fale    = registry.records['mpdg.govbr.faleconosco.controlpanel.IFaleSettings.admfale'].value
        responsavel = adm_fale or u'idg'

        portal = api.portal.get()
        # os dados serão guardados no Annotation para serem recuperados mais tarde para a criacao do fale conosco
        annotation = IAnnotations(portal)
        dados_fale = {}
        try:
            fale = annotation[KEY_CONFIRMA]
        except KeyError:
            fale = []
        hash = hashlib.sha1(str(random.random())).hexdigest()

        dados_fale['hash'] = hash
        conteudo = {
            'nome': nome,
            'email': email,
            'assunto': assunto,
            'mensagem': mensagem,
            'responsavel': responsavel,
        }
        dados_fale['conteudo'] = conteudo
        fale.append(dados_fale)
        annotation[KEY_CONFIRMA] = fale
        
        url_confirm = portal.absolute_url() + '/fale_confirma?h=' + hash

        endereco = email
        texto = EMAIL_FALE % (nome,assunto,mensagem,email, url_confirm)
        mensagem = prepare_email_message(texto, html=True)
        simple_send_mail(mensagem, endereco, assunto)

        dados = urllib.urlencode(conteudo)
        contextURL = "{0}/@@confirmacao?{1}".format(self.context.absolute_url(), dados)
        self.request.response.redirect(contextURL)
