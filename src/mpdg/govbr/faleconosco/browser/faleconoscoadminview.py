# -*- coding: utf-8 -*-
from five import grok
from datetime import date, datetime, timedelta
from DateTime import DateTime
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from AccessControl import Unauthorized
from mpdg.govbr.faleconosco.config import DIAS_PRAZO, DIAS_ATRASO, DIAS_ALERTA
from mpdg.govbr.faleconosco.interfaces import IFaleConosco
from mpdg.govbr.faleconosco.browser.utilities import FaleConoscoAdminRequired

grok.templatedir('templates')

class FaleConoscoAdminView(FaleConoscoAdminRequired, grok.View):
    """ View para administracao do Fale Conosco
    """
    grok.name('fale-conosco-admin')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    def update(self):

        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', True)
        self.logged_user = api.user.get_current().id
        return super(FaleConoscoAdminView, self).update()

    def fale_conosco(self):
        # metodo que retornara os objetos do tipo FaleConosco

        catalog     = api.portal.get_tool('portal_catalog')
        request     = self.request
        query       = {}
        assunto     = request.form.get('assunto', None)
        responsavel = request.form.get('responsavel', None)
        tipo        = request.form.get('tipo', None)

        query['object_provides'] = IFaleConosco.__identifier__
        query['review_state']    = ['encaminhado', 'novo', 'resgatado', 'respondido']
        query['sort_on']         = 'Date'
        query['sort_order']      = 'reverse'
        query['arquivado']       = False

        if tipo:

            hoje        = datetime.today()
            prazo       = datetime.fromordinal(hoje.toordinal()- DIAS_PRAZO)
            alerta      = datetime.fromordinal(prazo.toordinal()- DIAS_ALERTA)
            query_range = {}

            if tipo != 'todos':
                query['review_state'] = ['encaminhado', 'novo', 'resgatado']

            if tipo == 'prazo':
                query_range = {'query': (prazo, hoje), 'range': 'min:max'}

            if tipo == 'alerta':
                fim = datetime.fromordinal(prazo.toordinal()- 1)
                query_range = {'query': (alerta, fim), 'range': 'min:max'}

            if tipo == 'atraso':
                fim = datetime.fromordinal(alerta.toordinal()- 1)
                query_range = {'query': (datetime(2010,1,1,0,0,0), fim), 'range':'min:max'}

            if tipo == 'respondido':
                query['review_state'] = 'respondido'

            if query_range:
                query['created'] = query_range


        if 'inicio' in request.form.keys() or 'termino' in request.form.keys():

            query_range = {}
            inicio      = request.form.get('inicio', None)
            termino     = request.form.get('termino', None)

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

        busca = catalog.unrestrictedSearchResults(query)  # busca no banco pelos dados filtrados

        resultado = []  # TODO: refatorar e incluir o codigo abaixo em outro metodo
        for item in busca:  # Criação do dicionário para exibir os resultados no template
            obj = item.getObject()
            item_dict = {}
            item_dict['data'] = item.created.strftime('%d/%m/%Y')
            item_dict['assunto'] = obj.getAssunto()
            item_dict['nome'] = obj.getNome()
            item_dict['responsavel'] = obj.getResponsavel()
            item_dict['uid'] = item.UID
            item_dict['status'] = self.get_status(item)
            item_dict['path'] = '/'.join(obj.getPhysicalPath())
            item_dict['categorias'] = ', '.join(obj.Subject())

            resultado.append(item_dict)

        return resultado

    def get_status(self, conteudo):
        """metodo para verificar o status da mensagem"""
        hoje        = datetime.today()
        prazo       = datetime.fromordinal(hoje.toordinal()- DIAS_PRAZO)
        alerta      = datetime.fromordinal(prazo.toordinal()- DIAS_ALERTA)
        atraso      = datetime.fromordinal(alerta.toordinal()- DIAS_ATRASO)
        data        = conteudo.created.asdatetime().replace(tzinfo=None)

        fimalerta = prazo - timedelta(1)

        status = ''
        if conteudo.review_state == 'respondido':
            status = 'respondido'

        elif (data >= prazo) and (data <= hoje):
            status = 'prazo'

        elif (data >= alerta) and (data <= fimalerta):
            status = 'alerta'

        else:
            status = 'atraso'

        return status

    def get_assunto(self, conteudo):
        """metodo para buscar o titulo do assunto"""
        factory = getUtility(IVocabularyFactory, u'mpdg.govbr.faleconosco.Assuntos')
        vocab   = factory(self.context)
        termo   = conteudo.getObject().getAssunto()

        try:
            assunto = vocab.getTerm(termo)
            return assunto.title
        except LookupError:
            return ''

    def assuntos(self):
        """metodo para retornar os assuntos"""
        factory = getUtility(IVocabularyFactory, u'mpdg.govbr.faleconosco.Assuntos')
        vocab = factory(self.context)

        return vocab._terms

    def get_responsaveis_filtro(self):
        """metodo para retornar os responsaveis"""
        usuarios_fale      = api.user.get_users(groupname="adm-fale-conosco")
        lista_responsaveis = []

        for usuario in usuarios_fale:

            responsavel         = {}
            responsavel['id']   = usuario.id
            responsavel['nome'] = api.user.get(username=usuario.id).getProperty('fullname')
            lista_responsaveis.append(responsavel)
            # responsaveis = catalog.uniqueValuesFor('responsavel')

        return lista_responsaveis

    def can_reply(self, estado, resp):
        """Retorna True se o estado do objeto não for 'respondido', se o usuário
        logado for adm do fale conosco ou se o usuário logado é o responsável da mensagem
        """
        if estado != 'respondido':
            if self.logged_user == self.get_adm_fale() or self.logged_user == resp:
                return True
        return False

    def get_responder_url(self, msgresp, uid):
        """Se o usuário for o adm do fale conosco ele pode responder por email
        diretamente ao usuário, então ele irá para a view @@responder-selecionados.
        Caso ele seja apenas um usuário comum do fale consoco, o que ele pode fazer
        é encaminhar a mensagem para o admin do fale, na view @@encaminhar-admin-view
        """
        result = ''
        if self.logged_user == self.get_adm_fale():
            # se usuario logado é admin do fale
            result = '@@responder-selecionados?uids={0}'.format(uid)
        elif self.logged_user == msgresp:
            # se não, se o usuario é o responsavel da msg
            result = '@@encaminhar-admin-view?uids={0}'.format(uid)
        return result

    def get_adm_fale(self):
        """
        Retorna o usuário administrador do fale conosco.
        """
        registry = getUtility(IRegistry)
        adm_fale = registry.records['mpdg.govbr.faleconosco.controlpanel.IFaleSettings.admfale'].value
        return adm_fale

    def is_admin(self):
        """
        metodo para pegar o usuário logado e chegar se ele é
        o administrador do Fale Conosco
        """
        adm_fale = self.get_adm_fale()
        if self.logged_user == adm_fale:
            return True
        return False

    def is_user(self):
        adm_fale = self.get_adm_fale()
        if self.logged_user != adm_fale:
            return True
        return False

    def can_rescue(self, fale, estado):
        if estado == 'encaminhado':
            if self.is_admin():
                return True

            catalog = api.portal.get_tool('portal_catalog')
            brain = catalog.searchResults(
                portal_type = 'Mensagem',
                path = fale['path'],
                sort_limit = 1,
                sort_on = 'created',
                sort_order = "reverse"
            )[:1]

            if brain:
                item = brain[0]
                obj = item.getObject()
                responsavel = obj.getResponsavel()

                if self.logged_user == responsavel:
                    return True
                else:
                    return False

        return False
