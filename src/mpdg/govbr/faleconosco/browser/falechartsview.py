# -*- coding: utf-8 -*-

import pandas as pd
from pandas.tseries.offsets import BDay

from DateTime import DateTime

from five import grok

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from mpdg.govbr.faleconosco.config import DIAS_PRAZO, DIAS_ATRASO, DIAS_ALERTA
from mpdg.govbr.faleconosco.interfaces import IFaleConosco

grok.templatedir('templates')


class FaleChartsView(grok.View):
    """ view para os gráficos
    """

    grok.name('fale-conosco-charts')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    no_prazo = 0
    alerta = 0
    atraso = 0
    respondido = 0

    def update(self, **kwargs):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)

    def fale_conosco(self):
        """ metodo que retornara os objetos do tipo FaleConosco
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        request = self.request

        # parametros da busca
        assunto = request.form.get('assunto', None)
        responsavel = request.form.get('responsavel', None)
        prazo = request.form.get('prazo', None)
        alerta = request.form.get('alerta', None)
        atraso = request.form.get('atraso', None)
        respondido = request.form.get('respondido', None)

        query = {}

        query['object_provides'] = IFaleConosco.__identifier__

        if 'inicio' in request.form.keys() or 'termino' in request.form.keys():
            query_range = {}
            inicio = request.form.get('inicio', None)
            termino = request.form.get('termino', None)

            if inicio:
                inicio = '%s/%s/%s' % (inicio[6:], inicio[3:5], inicio[:2])
                inicio = DateTime(inicio)

            if termino:
                termino = '%s/%s/%s' % (termino[6:], termino[3:5], termino[:2])
                termino = DateTime(termino) + 1

            if inicio and termino:
                query_range = {'query': (inicio, termino), 'range': 'min:max'}
            elif not termino and inicio:
                query_range = {'query': inicio, 'range': 'min'}
            elif not inicio and termino:
                query_range = {'query': termino, 'range': 'max'}

            if query_range:
                query['created'] = query_range

        if assunto:
            query['assunto'] = assunto

        if responsavel:
            query['responsavel'] = responsavel

        if respondido:
            query['review_state'] = 'respondido'

        busca = catalog(query)

        resultado = []
        for item in busca:
            item_dict = {}
            if prazo and self.get_status(item) == 'prazo':
                self.no_prazo += 1
                item_dict['status'] = 'prazo'
                item_dict['data'] = item.created.strftime('%d/%m/%Y')
                item_dict['assunto'] = self.get_assunto(item)
                item_dict['nome'] = item.getObject().getNome()
                item_dict['responsavel'] = item.getObject().getResponsavel()
                item_dict['uid'] = item.UID
            elif alerta and self.get_status(item) == 'alerta':
                self.alerta += 1
                item_dict['status'] = 'alerta'
                item_dict['data'] = item.created.strftime('%d/%m/%Y')
                item_dict['assunto'] = self.get_assunto(item)
                item_dict['nome'] = item.getObject().getNome()
                item_dict['responsavel'] = item.getObject().getResponsavel()
                item_dict['uid'] = item.UID
            elif atraso and self.get_status(item) == 'atraso':
                self.atraso += 1
                item_dict['status'] = 'atraso'
                item_dict['data'] = item.created.strftime('%d/%m/%Y')
                item_dict['assunto'] = self.get_assunto(item)
                item_dict['nome'] = item.getObject().getNome()
                item_dict['responsavel'] = item.getObject().getResponsavel()
                item_dict['uid'] = item.UID
            elif respondido and self.get_status(item) == 'respondido':
                self.respondido += 1
                item_dict['status'] = 'respondido'
                item_dict['data'] = item.created.strftime('%d/%m/%Y')
                item_dict['assunto'] = self.get_assunto(item)
                item_dict['nome'] = item.getObject().getNome()
                item_dict['responsavel'] = item.getObject().getResponsavel()
                item_dict['uid'] = item.UID
            elif not prazo and not alerta and not atraso and not respondido:
                if self.get_status(item) == 'respondido':
                    self.respondido += 1
                if self.get_status(item) == 'prazo':
                    self.no_prazo += 1
                if self.get_status(item) == 'alerta':
                    self.alerta += 1
                if self.get_status(item) == 'atraso':
                    self.atraso += 1
                item_dict['status'] = self.get_status(item)
                item_dict['data'] = item.created.strftime('%d/%m/%Y')
                item_dict['assunto'] = self.get_assunto(item)
                item_dict['nome'] = item.getObject().getNome()
                item_dict['responsavel'] = item.getObject().getResponsavel()
                item_dict['uid'] = item.UID
            if item_dict:
                resultado.append(item_dict)

        return resultado

    def get_status(self, conteudo):
        # metodo para verificar o status da mensagem

        hoje = pd.datetime.today()
        prazo = hoje - BDay(DIAS_PRAZO)
        alerta = hoje - BDay(DIAS_ALERTA)
        atraso = hoje - BDay(DIAS_ATRASO)

        data = conteudo.created
        if conteudo.review_state == 'respondido':
            return 'respondido'

        if prazo.to_datetime().date() <= data.asdatetime().date():
            return 'prazo'

        if alerta.to_datetime().date() <= data.asdatetime().date() and prazo.to_datetime().date() > data.asdatetime().date():
            return 'alerta'

        if atraso.to_datetime().date() >= data.asdatetime().date():
            return 'atraso'

    def get_assunto(self, conteudo):
        # metodo para buscar o titulo do assunto

        factory = getUtility(IVocabularyFactory, u'mpdg.govbr.faleconosco.Assuntos')
        vocab = factory(self.context)

        termo = conteudo.getObject().getAssunto()
        try:
            assunto = vocab.getTerm(termo)
            return assunto.title
        except LookupError:
            return ''

    def quantidade(self):
        prazo = self.no_prazo
        alerta = self.alerta
        atraso = self.atraso
        respondido = self.respondido

        return prazo + alerta + atraso + respondido
