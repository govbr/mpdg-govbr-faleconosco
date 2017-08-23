# -*- coding: utf-8 -*-
"""XHTML Compressor
"""

from plone.memoize.interfaces import IXHTMLCompressor
from zope.component import queryUtility
from zope.interface import implementer

SLIMMER = True
try:
    from slimmer import xhtml_slimmer
except ImportError:
    SLIMMER = False


def xhtml_compress(string):
    util = queryUtility(IXHTMLCompressor)
    if util is not None:
        return util.compress(string)
    return string


@implementer(IXHTMLCompressor)
class XHTMLSlimmer(object):

    def compress(self, string):
        if SLIMMER:
            return xhtml_slimmer(string)
        return string

xhtmlslimmer = XHTMLSlimmer()
