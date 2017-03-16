# -*- coding: utf-8 -*-

from zope.interface import implements

from Products.ATContentTypes.content.base import ATContentTypeSchema, ATCTContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

from mpdg.govbr.faleconosco.interfaces import IHistorico
from DateTime.DateTime import DateTime
from mpdg.govbr.faleconosco.config import PROJECTNAME
from mpdg.govbr.faleconosco import MessageFactory as _

HistoricoSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='nome',
        required=True,
        widget=atapi.StringWidget(
            label=_(u"Nome:"),
            description=_(u"")
        ),
    ),

    atapi.TextField(
        name='observacao',
        required=True,
        storage=atapi.AnnotationStorage(migrate=True),
        widget=atapi.TextAreaWidget(
            label=_(u"Observação:"),
            description=_(u""),
            rows=5,
        ),
    ),

    atapi.StringField(
        name='estado',
        required=True,
        # default=False,
        # storage=atapi.AnnotationStorage(migrate=False),
    ),

    atapi.DateTimeField('dataenvio',
        required = True,
        default_method = 'getDefaultTime',
    ),

))

schemata.finalizeATCTSchema(HistoricoSchema)


class Historico(ATCTContent):
    """ Classe do conteudo Historico
    """

    implements(IHistorico)

    meta_type = "Historico"
    schema = HistoricoSchema

    def getDefaultTime(self):  # function to return the current date and time
        return DateTime()

atapi.registerType(Historico, PROJECTNAME)
