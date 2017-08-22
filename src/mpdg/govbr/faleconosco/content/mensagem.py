# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.ATContentTypes.content.base import ATContentTypeSchema, ATCTContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

from mpdg.govbr.faleconosco.interfaces import IMensagem
from mpdg.govbr.faleconosco.config import PROJECTNAME
from mpdg.govbr.faleconosco import MessageFactory as _

MensagemSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='nome',
        required=True,
        widget=atapi.StringWidget(
            label=_(u"Nome"),
            description=_(u"")
        ),
    ),

    atapi.StringField(
        name='assunto',
        required=True,
        widget=atapi.StringWidget(
            label=_(u"Assunto"),
            description=_(u"")
        ),
    ),

    atapi.StringField(
        name='email',
        required=True,
        widget=atapi.StringWidget(
            label=_(u"E-mail"),
            description=_(u"")
        ),
    ),

    atapi.StringField(
        name='responsavel',
        required=False,
        widget=atapi.StringWidget(
            label=_(u"Responsavel"),
            description=_(u"")
        ),
    ),

    atapi.TextField(
        name='mensagem',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(migrate=True),
        widget=atapi.TextAreaWidget(
            label=_(u"Mensagem"),
            description=_(u""),
            rows=5,
        ),
    ),

))

schemata.finalizeATCTSchema(MensagemSchema)


class Mensagem(ATCTContent):
    """ Classe do conteudo Mensagem
    """

    implements(IMensagem)

    meta_type = "Mensagem"
    schema = MensagemSchema

atapi.registerType(Mensagem, PROJECTNAME)
