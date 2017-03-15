# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from plone import api
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.archetypes import InplaceATFolderMigrator
from StringIO import StringIO

grok.templatedir('templates')


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

class FixBrokenObjects(grok.View):
    grok.name('fixbrokenobjects')
    grok.require('zope2.View')
    grok.context(Interface)

    def __call__(self):
        # catalog = api.portal.get_tool('portal_catalog')
        # brains = catalog.searchResults(UID='31aac804c7ae4e6cb04850267dd73613')
        # brain = brains[0]
        # obj = brain.getObject()
        # migrator = FaleConoscoBaseMigrator(obj)
        # migrator.migrate()
        # import transaction; transaction.commit()
        # return super(FixBrokenObjects, self).__call__()
        return self.migrate_all()

    def migrate_all(self):
        out = StringIO()
        print >> out, "Starting migration"

        portal = api.portal.get()
        migrators = (FaleConoscoBaseMigrator, )

        for migrator in migrators:
            walker = migrator.walkerClass(portal, migrator)
            walker.go(out=out)
            print >> out, walker.getOutput()

        print >> out, "Migration finished"
        import transaction; transaction.commit()
        return out.getvalue()
