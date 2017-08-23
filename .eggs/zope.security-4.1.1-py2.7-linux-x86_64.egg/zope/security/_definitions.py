##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Common definitions to avoid circular imports
"""
import threading
import zope.interface

from zope.security import interfaces
from zope.security._compat import _u

thread_local = threading.local()

@zope.interface.provider(interfaces.IPrincipal)
class system_user(object):
    id = _u('zope.security.management.system_user')
    title = _u('System')
    description = _u('')
