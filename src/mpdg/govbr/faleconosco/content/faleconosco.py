# -*- coding: utf-8 -*-
from zope.interface import implements
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from mpdg.govbr.faleconosco.interfaces import IFaleConosco
from mpdg.govbr.faleconosco.config import PROJECTNAME
from mpdg.govbr.faleconosco import MessageFactory as _

FaleConoscoSchema = ATFolderSchema.copy() + atapi.Schema((

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
        searchable=True,
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

    atapi.BooleanField(
        name='arquivado',
        required=False,
    ),

))

schemata.finalizeATCTSchema(FaleConoscoSchema)


class FaleConosco(ATFolder):
    """ Classe do conteudo FaleConosco
    """

    implements(IFaleConosco)

    meta_type = "FaleConosco"
    schema = FaleConoscoSchema

    _at_rename_after_creation = True

atapi.registerType(FaleConosco, PROJECTNAME)
