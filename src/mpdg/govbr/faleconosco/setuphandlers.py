# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone import api
import logging
from mpdg.govbr.faleconosco.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName


logger = logging.getLogger(PROJECTNAME)

@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'mpdg.govbr.faleconosco:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

def create_groups(portal):
    portal = api.portal.get()
    api.group.create(
        groupname='adm-fale-conosco',
        title='Administradores Fale Conosco',
        description='Usuários com permissão de acesso ao Painel de \
                     Controle do Fale Conosco',
    )

    logger.info("Criado grupo Administradores Fale Conosco")


def create_faq(portal):
    portal = api.portal.get()
    if not 'faq' in portal:
        obj = api.content.create(
            type='Folder',
            id='faq',
            title='FAQ - Fale conosco',
            container= portal
        )

        obj_example= api.content.create(
        type='Document',
        title='Exemplo FAQ',
        description= 'Exemplo de documento do FAQ',
        container= obj
        )


def create_folder_fale(portal):
    portal = api.portal.get()
    # fale_folder = getattr(portal,'fale-conosco',None)
    if 'fale-conosco' not in portal:
        obj_fale = api.content.create(

            type='Folder',
            title='Fale Conosco',
            description='Pasta para armazenar o fale conosco',
            container= portal
        )
        obj_fale.setLayout('@@fale-conosco')
        return obj_fale

def create_link(portal):
    portal = api.portal.get()
    servicos = portal['servicos']
    if 'fale-conosco' not in servicos:
        link_fale = api.content.create(
            type='Link',
            remoteUrl='${portal_url}/fale-conosco/@@fale-conosco',
            title='Fale Conosco',
            container= portal['servicos']
    )


def create_textos_prontos(portal):
    portal = api.portal.get()
    # textos = getattr(portal, 'textos-prontos' ,None )
    if 'textos-prontos' not in portal:

        obj_texto = api.content.create(
            type='Folder',
            title='Textos Prontos',
            container= portal,
            description='Pasta pra armazenar textos prontos',
        )

        obj_example_textos= api.content.create(
            type='Document',
            title='Exemplo textos-prontos',
            description= 'Exemplo de documento de Textos Prontos',
            container= obj_texto
            )


def create_link_portal(portal):
    portal = api.portal.get()
    # obj_link= getattr(portal, 'sistema-fale-conosco' ,None )
    if 'sistema-fale-conosco' not in portal:
        obj_link_portal = api.content.create(
            type='Folder',
            title='Sistema Fale Conosco',
            container = portal

    )

        link_painel_adm = api.content.create(
            type='Link',
            title='Painel de Administração',
            remoteUrl='${portal_url}/@@fale-conosco-admin',
            container=portal['sistema-fale-conosco']
    )


        link_cadrastro_faq = api.content.create(
            type='Link',
            title='Cadastrar Perguntas Frequentes ',
            remoteUrl='${portal_url}/faq',
            container=portal['sistema-fale-conosco']
    )


class Empty:
    pass


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('mpdg.govbr.faleconosco')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    # setup = getToolByName(context, 'portal_setup')
    setup = api.portal.get_tool('portal_setup')
    PROFILE_ID = 'profile-mpdg.govbr.faleconosco:default'
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = api.portal.get_tool('portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (
        ('assunto', 'ZCTextIndex'),
        ('arquivado', 'BooleanIndex'),
    )

    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            if meta_type == 'ZCTextIndex':
                item_extras = Empty()
                item_extras.doc_attr = name
                item_extras.index_type = 'Okapi BM25 Rank'
                item_extras.lexicon_id = 'plone_lexicon'
                catalog.addIndex(name, meta_type, item_extras)
            else:
                catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)
