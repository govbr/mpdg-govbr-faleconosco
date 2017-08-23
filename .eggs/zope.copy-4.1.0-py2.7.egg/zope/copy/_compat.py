##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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

import sys

PY3 = sys.version_info[0] >= 3

try:
    from cPickle import Pickler
    from cPickle import Unpickler
except ImportError:
    from pickle import Pickler
    from pickle import Unpickler

if PY3:
    def _memo(pickler):
        # Python 3 uses a "PicklerMemoProxy" which is not subscriptable
        # by itself
        return pickler.memo.copy()
else:
    from operator import attrgetter

    _memo = attrgetter('memo')

def _get_pid(pickler, oid):
    return _memo(pickler)[oid][0]

def _get_obj(unpickler, pid):
    return _memo(unpickler)[pid]
