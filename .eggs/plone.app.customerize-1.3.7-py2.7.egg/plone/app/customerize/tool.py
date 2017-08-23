# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from five.customerize.interfaces import IViewTemplateContainer
from OFS.Folder import Folder
from Products.CMFCore.permissions import ManagePortal
from zope.interface import implementer


@implementer(IViewTemplateContainer)
class ViewTemplateContainer(Folder):
    """ a local utility storing all ttw view templates provided
        by five.customerize in a folder """

    id = 'portal_view_customizations'
    title = 'Manages view customizations'
    meta_type = 'Plone View Customizations'

    security = ClassSecurityInfo()

    manage_options = (
        dict(label='Registrations', action='registrations.html'),
    ) + Folder.manage_options[0:1] + Folder.manage_options[2:]

    @security.protected(ManagePortal)
    def addTemplate(self, id, template):
        """ add the given ttw view template to the container """
        self._setObject(id, template)
        return getattr(self, id)

InitializeClass(ViewTemplateContainer)
