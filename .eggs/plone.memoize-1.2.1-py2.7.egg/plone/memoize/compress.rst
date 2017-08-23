XHTML Compressor
================

In order to use Peter Bengtsson's slimmer library available from http://www.issuetrackerproduct.com/Download#slimmer you need to register the XHTMLSlimmer utility like this::

  <utility component="plone.memoize.compress.xhtmlslimmer"
           provides="plone.memoize.interfaces.IXHTMLCompressor" />

Make necessary imports::

    >>> from plone.memoize.compress import xhtml_compress
    >>> from plone.memoize.interfaces import IXHTMLCompressor
    >>> from zope.interface import implementer


You can register other XHTML-whitespace removal libraries as well.

Per default there is no compressor available and we get the same string back::

    >>> html_string = u"<html><body><SPAN>Hello.</SPAN></body><html>"
    >>> xhtml_compress(html_string) is html_string
    True

Make a stupid lowercasing compressor.
This is not safe as it would lowercase all text outside of tags as well::

    >>> @implementer(IXHTMLCompressor)
    ... class LowerCaser(object):
    ...
    ...     def compress(self, string):
    ...         return string.lower()

    >>> lower = LowerCaser()

Register our new compressor::

    >>> from zope.component import getSiteManager
    >>> sm = getSiteManager()
    >>> sm.registerUtility(lower)

    >>> str(xhtml_compress(html_string))
    '<html><body><span>hello.</span></body><html>'

