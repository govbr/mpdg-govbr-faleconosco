# -*- coding: utf-8 -*-

from five import grok
from datetime import datetime

from plone import api
from plone.i18n.normalizer import idnormalizer

from zope.annotation import IAnnotations
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from mpdg.govbr.faleconosco.setuphandlers import create_folder_fale
from mpdg.govbr.faleconosco import MessageFactory as _
from mpdg.govbr.faleconosco.config import KEY_CONFIRMA

grok.templatedir('templates')


class FaleConfirma(grok.View):
    """ view para confirmar o fale conosco e criar o conteudo
    """
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('fale_confirma')

    def update(self, **kwargs):
        self.request.set('disable_border', True)

    def render(self, **kwargs):
        self.update()
        hash = self.request.get('h', None)
        self.portal = api.portal.get()

        try:
            fale = self.portal['fale-conosco']
        except KeyError:
            fale = create_folder_fale(self.portal)

        annotation = IAnnotations(self.portal)
        self.fale = annotation[KEY_CONFIRMA]
        dados = [m for m in self.fale if hash == m['hash']]
        if dados:
            conteudo = dados[0]['conteudo']
            nome = conteudo['nome']
            email = conteudo['email']
            assunto = conteudo['assunto']
            mensagem = conteudo['mensagem']
            responsavel = conteudo['responsavel']

            id = idnormalizer.normalize(nome) + '-' + str(datetime.now().microsecond)

            # tool para criacao do conteudo
            pt = getToolByName(self.context, 'portal_types')
            type_info = pt.getTypeInfo('FaleConosco')
            fconosco = type_info._constructInstance(fale, id)
            fconosco.setTitle(nome)
            fconosco.setNome(nome)
            fconosco.setEmail(email)
            fconosco.setAssunto(assunto)
            fconosco.setMensagem(mensagem)
            fconosco.setResponsavel(responsavel)
            fconosco.reindexObject()

            self.fale.remove(dados[0])
            annotation[KEY_CONFIRMA] = self.fale

            IStatusMessage(self.request).addStatusMessage(
                _(u"Sua confirmação foi realizada com sucesso!"), type='info')
        else:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Não existe nenhuma mensagem para ser confirmada"), type='error')
        return self.request.response.redirect(self.portal.absolute_url())
