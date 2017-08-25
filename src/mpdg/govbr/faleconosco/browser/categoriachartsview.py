# -*- coding: utf-8 -*-
import operator
import random
from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot

from mpdg.govbr.faleconosco.browser import falecategorizar

grok.templatedir('templates')


class CategoriaChartsView(grok.View):
    """ view para os gráficos
    """

    grok.name('categoria-charts-view')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self):
        qtd_get = int(self.request.form.get('qtd', 10))
        self.qtd = qtd_get if qtd_get >= 0 else 0
        self.tagdict = self.get_tags_dict()
        self.taglist = self.get_tags_list()
        self.tagdata = self.get_tags_data()
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)

    def get_tags_dict(self):
        """ metodo que retorna um dicionario com as tags e a quantidade de usos dela
        {
           'TI': 4, 'COPPE': 10
        }
        """
        catalog = api.portal.get_tool('portal_catalog')
        tags = list(catalog.uniqueValuesFor('Subject'))
        portal = api.portal.get()
        path = '/'.join(portal.getPhysicalPath()) + '/fale-conosco/'
        tagdict = {}
        for tag in tags:
            brains = catalog.searchResults(
                portal_type='FaleConosco',
                Subject=tag,
                path=path
            )
            qtd_tags = len(brains)
            tagdict[tag] = qtd_tags
        return tagdict

    def get_tags_list(self):
        """Retorna uma lista de tags
            ['apple', 'orange', ...]
        """
        tags = self._filter_tags()
        result = []
        for tag, v in tags:
            result.append(tag)
        return result

    def get_tags_data(self):
        """
        Retorna uma lista com a quantidade de objetos por tag
        (lista -> self.get_tags_list)
        [2, 3, 4, 1, 5, ...]
        """
        result = []
        for tag in self.taglist:
            result.append(self.tagdict[tag])
        return result

    def zipped_tags(self):
        return zip(self.taglist, self.tagdata)

    def total_obj(self):
        return sum(self.tagdata)

    def _filter_tags(self):
        """
        Filtra a quantidade de tags que serão exibidas de acordo com
        a variável de instância self.qtd
        """
        taglist = sorted(
            self.tagdict.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        return taglist[:self.qtd]

    def gera_cor(self):
        """
        Gera uma lista de cores de tamanho N, onde N é a quantidade de elementos exibidos (self.qtd)
        """
        result = []
        for elem in range(0, self.qtd):
            cor = '#{:02x}{:02x}{:02x}'.format(*map(lambda x: random.randint(0, 255), range(0,10)))
            result.append(cor)
        return result

