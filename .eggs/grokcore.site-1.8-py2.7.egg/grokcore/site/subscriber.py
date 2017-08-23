##############################################################################
#
# Copyright (c) 2006-2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.site import LocalSiteManager
from zope.site.site import _findNextSiteManager

import grokcore.component
from grokcore.site.components import Site


@grokcore.component.subscribe(Site, IObjectAddedEvent)
def addSiteHandler(site, event):
    """Add a local site manager to a Grok site object upon its creation.
    """
    if event.oldParent is not None:
        return
    sitemanager = LocalSiteManager(site)
    del sitemanager['default']
    site.setSiteManager(sitemanager)


@grokcore.component.subscribe(Site, IObjectRemovedEvent)
def removeSiteHandler(site, event):
    """Cleanup a after a site was removed.
    """
    if event.newParent is not None:
        # Please note that the code for moving a site is properly implemented
        # inside zope.site.
        return
    local = site.getSiteManager()
    parent = _findNextSiteManager(site)
    if parent is not None:
        parent.removeSub(local)
