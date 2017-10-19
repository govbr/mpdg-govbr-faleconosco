# -*- coding: utf-8 -*-

from five import grok
from mpdg.govbr.faleconosco.interfaces import IAssunto
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class Assuntos(object):
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        catalog = getToolByName(context, 'portal_catalog')
        assuntos = catalog(object_provides=IAssunto.__identifier__)
        itens = []
        for brain in assuntos:
            itens.append(
                SimpleTerm(value=brain.id, title=brain.Title)
            )

        return SimpleVocabulary(itens)

grok.global_utility(Assuntos, name=u'mpdg.govbr.faleconosco.Assuntos')
