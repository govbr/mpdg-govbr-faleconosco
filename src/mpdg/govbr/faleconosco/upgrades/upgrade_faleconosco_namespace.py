#-*- coding: utf-8 -*-
import logging
from plone import api
from Products.contentmigration.archetypes import InplaceATFolderMigrator
from Products.contentmigration.basemigrator.walker import CatalogWalker
from StringIO import StringIO

from mpdg.govbr.faleconosco.config import PROJECTNAME


logger = logging.getLogger(PROJECTNAME)


class HistoricoBaseMigrator(InplaceATFolderMigrator):
    walkerClass = CatalogWalker
    src_portal_type = 'Historico'
    src_meta_type = 'Historico'
    dst_portal_type = 'Historico'
    dst_meta_type = 'Historico'

    def custom(self):
        self.new.setCreationDate(self.old.created())
        self.new.reindexObject()


class MensagemBaseMigrator(InplaceATFolderMigrator):
    walkerClass = CatalogWalker
    src_portal_type = 'Mensagem'
    src_meta_type = 'Mensagem'
    dst_portal_type = 'Mensagem'
    dst_meta_type = 'Mensagem'

    def custom(self):
        self.new.setCreationDate(self.old.created())
        self.new.reindexObject()


class FaleConoscoBaseMigrator(InplaceATFolderMigrator):
    walkerClass = CatalogWalker
    src_portal_type = 'FaleConosco'
    src_meta_type = 'FaleConosco'
    dst_portal_type = 'FaleConosco'
    dst_meta_type = 'FaleConosco'

    def custom(self):
        self.new.setCreationDate(self.old.created())
        self.new.reindexObject()


def upgrade_fale_conosco(context):
    out = StringIO()
    print >> out, "Starting migration"

    portal = api.portal.get()
    migrators = (FaleConoscoBaseMigrator, HistoricoBaseMigrator, MensagemBaseMigrator)

    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        print >> out, walker.getOutput()

    print >> out, "Migration finished"
    import transaction; transaction.commit()
    logger.info(out.getvalue())
