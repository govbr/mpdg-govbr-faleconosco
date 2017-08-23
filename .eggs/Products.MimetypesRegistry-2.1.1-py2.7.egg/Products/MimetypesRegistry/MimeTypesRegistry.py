# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import InitializeClass
from BTrees.OOBTree import OOBTree
from OFS.Folder import Folder
from Persistence import PersistentMapping
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject
from Products.MimetypesRegistry.encoding import guess_encoding
from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.interfaces import IMimetype
from Products.MimetypesRegistry.interfaces import IMimetypesRegistry
from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
from Products.MimetypesRegistry.interfaces import ISourceAdapter
from Products.MimetypesRegistry.interfaces import MimeTypeException
from Products.MimetypesRegistry.mime_types import initialize
from Products.MimetypesRegistry.mime_types import magic
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.contenttype import guess_content_type
from zope.interface import implementer

import fnmatch
import logging
import os
import re


logger = logging.getLogger(__name__)


suffix_map = {
    'tgz': '.tar.gz',
    'taz': '.tar.gz',
    'tz': '.tar.gz',
}

encodings_map = {
    'gz': 'gzip',
    'Z': 'compress',
}

_www = os.path.join(os.path.dirname(__file__), 'www')


@implementer(IMimetypesRegistry, ISourceAdapter)
class MimeTypesRegistry(UniqueObject, ActionProviderBase, Folder):
    """Mimetype registry that deals with
    a) registering types
    b) wildcarding of rfc-2046 types
    c) classifying data into a given type
    """

    id = 'mimetypes_registry'
    meta_type = 'MimeTypes Registry'
    isPrincipiaFolderish = 1  # Show up in the ZMI

    meta_types = all_meta_types = (
        {'name': 'MimeType',
         'action': 'manage_addMimeTypeForm'},
    )

    manage_options = (
        ({'label': 'MimeTypes',
            'action': 'manage_main'},) +
        Folder.manage_options[2:]
    )

    manage_addMimeTypeForm = PageTemplateFile('addMimeType', _www)
    manage_main = PageTemplateFile('listMimeTypes', _www)
    manage_editMimeTypeForm = PageTemplateFile('editMimeType', _www)

    security = ClassSecurityInfo()

    # FIXME
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, id=None):
        if id is not None:
            assert id == self.id
        self.encodings_map = encodings_map.copy()
        self.suffix_map = suffix_map.copy()
        # Major key -> minor IMimetype objects
        self._mimetypes = PersistentMapping()
        # ext -> IMimetype mapping
        self.extensions = PersistentMapping()
        # glob -> (regex, mimetype) mapping
        self.globs = OOBTree()
        self.manage_addProperty('defaultMimetype', 'text/plain', 'string')
        self.manage_addProperty('unicodePolicies', 'strict ignore replace',
                                'tokens')
        self.manage_addProperty(
            'unicodePolicy',
            'unicodePolicies',
            'selection')
        self.manage_addProperty('fallbackEncoding', 'latin1', 'string')

        # initialize mime types
        initialize(self)
        self._new_style_mtr = 1

    @security.protected(ManagePortal)
    def register(self, mimetype):
        """ Register a new mimetype

        mimetype must implement IMimetype
        """
        mimetype = aq_base(mimetype)
        assert IMimetype.providedBy(mimetype)
        for t in mimetype.mimetypes:
            self.register_mimetype(t, mimetype)
        for extension in mimetype.extensions:
            self.register_extension(extension, mimetype)
        for glob in mimetype.globs:
            self.register_glob(glob, mimetype)

    @security.protected(ManagePortal)
    def register_mimetype(self, mt, mimetype):
        major, minor = split(mt)
        if not major or not minor or minor == '*':
            raise MimeTypeException('Can\'t register mime type %s' % mt)
        group = self._mimetypes.setdefault(major, PersistentMapping())
        if minor in group:
            if group.get(minor) != mimetype:
                logger.warn(
                    'Redefining mime type {0} ({1})'.format(
                        mt,
                        mimetype.__class__
                    )
                )
        group[minor] = mimetype

    @security.protected(ManagePortal)
    def register_extension(self, extension, mimetype):
        """ Associate a file's extension to a IMimetype

        extension is a string representing a file extension (not
        prefixed by a dot) mimetype must implement IMimetype
        """
        mimetype = aq_base(mimetype)
        if extension in self.extensions:
            if self.extensions.get(extension) != mimetype:
                logger.warn(
                    'Redefining extension {0} from {1} to {2}'.format(
                        extension,
                        self.extensions[extension],
                        mimetype
                    )
                )
        # we don't validate fmt yet, but its ["txt", "html"]
        self.extensions[extension] = mimetype

    @security.protected(ManagePortal)
    def register_glob(self, glob, mimetype):
        """ Associate a glob to a IMimetype

        glob is a shell-like glob that will be translated to a regex
        to match against whole filename.
        mimetype must implement IMimetype.
        """
        globs = getattr(self, 'globs', None)
        if globs is None:
            self.globs = globs = OOBTree()
        mimetype = aq_base(mimetype)
        existing = globs.get(glob)
        if existing is not None:
            regex, mt = existing
            if mt != mimetype:
                logger.warn(
                    'Redefining glob {0} from {1} to {2}'.format(
                        glob,
                        mt,
                        mimetype
                    )
                )
        # we don't validate fmt yet, but its ["txt", "html"]
        pattern = re.compile(fnmatch.translate(glob))
        globs[glob] = (pattern, mimetype)

    @security.protected(ManagePortal)
    def unregister(self, mimetype):
        """ Unregister a new mimetype

        mimetype must implement IMimetype
        """
        assert IMimetype.providedBy(mimetype)
        for t in mimetype.mimetypes:
            major, minor = split(t)
            group = self._mimetypes.get(major, {})
            if group.get(minor) == mimetype:
                del group[minor]
        for e in mimetype.extensions:
            if self.extensions.get(e) == mimetype:
                del self.extensions[e]
        globs = getattr(self, 'globs', None)
        if globs is not None:
            for glob in mimetype.globs:
                existing = globs.get(glob)
                if existing is None:
                    continue
                regex, mt = existing
                if mt == mimetype:
                    del globs[glob]

    @security.public
    def mimetypes(self):
        """Return all defined mime types, each one implements at least
        IMimetype
        """
        res = {}
        for g in self._mimetypes.values():
            for mt in g.values():
                res[mt] = 1
        return [aq_base(mtitem) for mtitem in res.keys()]

    @security.public
    def list_mimetypes(self):
        """Return all defined mime types, as string"""
        return [str(mt) for mt in self.mimetypes()]

    @security.public
    def lookup(self, mimetypestring):
        """Lookup for IMimetypes object matching mimetypestring

        mimetypestring may have an empty minor part or containing a
        wildcard (*) mimetypestring may and IMimetype object (in this
        case it will be returned unchanged

        Return a list of mimetypes objects associated with the
        RFC-2046 name return an empty list if no one is known.
        """
        if IMimetype.providedBy(mimetypestring):
            return (aq_base(mimetypestring), )
        __traceback_info__ = (repr(mimetypestring), str(mimetypestring))
        major, minor = split(str(mimetypestring))
        group = self._mimetypes.get(major, {})
        if not minor or minor == '*':
            res = group.values()
        else:
            res = group.get(minor)
            if res:
                res = (res,)
            else:
                return ()
        return tuple([aq_base(mtitem) for mtitem in res])

    @security.public
    def lookupExtension(self, filename):
        """Lookup for IMimetypes object matching filename

        Filename maybe a file name like 'content.txt' or an extension
        like 'rest'

        Return an IMimetype object associated with the file's
        extension or None
        """
        base = None
        if filename.find('.') != -1:
            base, ext = os.path.splitext(filename)
            ext = ext[1:]  # remove the dot
            while ext in self.suffix_map:
                base, ext = os.path.splitext(base + self.suffix_map[ext])
                ext = ext[1:]  # remove the dot
        else:
            ext = filename

        if base is not None and ext in self.encodings_map:
            base, ext = os.path.splitext(base)
            ext = ext[1:]  # remove the dot

        result = aq_base(self.extensions.get(ext))
        if result is None:
            result = aq_base(self.extensions.get(ext.lower()))
        return result

    @security.public
    def globFilename(self, filename):
        """Lookup for IMimetypes object matching filename

        Filename must be a complete filename with extension.

        Return an IMimetype object associated with the glob's or None
        """
        globs = getattr(self, 'globs', {})
        for key in globs:
            glob, mimetype = globs[key]
            if glob.match(filename):
                return aq_base(mimetype)
        return None

    @security.public
    def lookupGlob(self, glob):
        globs = getattr(self, 'globs', None)
        if globs is not None:
            return aq_base(globs.get(glob))

    def _classifiers(self):
        return [mt for mt in self.mimetypes() if IClassifier.providedBy(mt)]

    @security.public
    def classify(self, data, mimetype=None, filename=None):
        """Classify works as follows:
        1) you tell me the rfc-2046 name and I give you an IMimetype
           object
        2) the filename includes an extension from which we can guess
           the mimetype
        3) we can optionally introspect the data
        4) default to self.defaultMimetype if no data was provided
           else to application/octet-stream of no filename was provided,
           else to text/plain

        Return an IMimetype object or None
        """
        mt = None
        if mimetype:
            mt = self.lookup(mimetype)
            if mt:
                mt = mt[0]
        elif filename:
            mt = self.lookupExtension(filename)
            if mt is None:
                mt = self.globFilename(filename)
        if data and not mt:
            for c in self._classifiers():
                if c.classify(data):
                    mt = c
                    break
            if not mt:
                mstr = magic.guessMime(data)
                if mstr:
                    _mt = self.lookup(mstr)
                    if len(_mt) > 0:
                        mt = _mt[0]
        if not mt:
            if not data:
                mtlist = self.lookup(self.defaultMimetype)
            elif filename:
                mtlist = self.lookup('application/octet-stream')
            else:
                failed = 'text/x-unknown-content-type'
                filename = filename or ''
                data = data or ''
                ct, enc = guess_content_type(filename, data, None)
                if ct == failed:
                    ct = 'text/plain'
                mtlist = self.lookup(ct)
            if len(mtlist) > 0:
                mt = mtlist[0]
            else:
                return None

        # Remove acquisition wrappers
        return aq_base(mt)

    def __call__(self, data, **kwargs):
        """ Return a triple (data, filename, mimetypeobject) given
        some raw data and optional paramters

        method from the isourceAdapter interface
        """
        mimetype = kwargs.get('mimetype', None)
        filename = kwargs.get('filename', None)
        encoding = kwargs.get('encoding', None)
        mt = None
        if hasattr(data, 'filename'):
            filename = os.path.basename(data.filename)
        elif hasattr(data, 'name'):
            filename = os.path.basename(data.name)

        if hasattr(data, 'read'):
            _data = data.read()
            if hasattr(data, 'seek'):
                data.seek(0)
            data = _data

        # We need to figure out if data is binary and skip encoding if
        # it is
        mt = self.classify(data, mimetype=mimetype, filename=filename)

        if not mt.binary and not isinstance(data, unicode):
            # if no encoding specified, try to guess it from data
            if encoding is None:
                encoding = self.guess_encoding(data)

            # ugly workaround for
            # https://sourceforge.net/tracker/?func=detail&aid=1068001&group_id=75272&atid=543430
            # covered by
            # https://sourceforge.net/tracker/?func=detail&atid=355470&aid=843590&group_id=5470
            # dont remove this code unless python is fixed.
            if encoding is "macintosh":
                encoding = 'mac_roman'

            try:
                try:
                    data = unicode(data, encoding, self.unicodePolicy)
                except (ValueError, LookupError):
                    # wrong unicodePolicy
                    data = unicode(data, encoding)
            except:
                data = unicode(data, self.fallbackEncoding)

        return (data, filename, aq_base(mt))

    @security.public
    def guess_encoding(self, data):
        """ Try to guess encoding from a text value.

        If no encoding can be guessed, fall back to utf-8.
        """
        if isinstance(data, unicode):
            # data maybe unicode but with another encoding specified
            data = data.encode('UTF-8')
        encoding = guess_encoding(data)
        if encoding is None:
            encoding = 'utf-8'
        return encoding

    @security.protected(ManagePortal)
    def manage_delObjects(self, ids, REQUEST=None):
        """ delete the selected mime types """
        for id in ids:
            self.unregister(self.lookup(id)[0])
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')

    @security.protected(ManagePortal)
    def manage_addMimeType(self, id, mimetypes, extensions, icon_path,
                           binary=0, globs=None, REQUEST=None):
        """add a mime type to the tool"""
        mt = MimeTypeItem(id, mimetypes, extensions=extensions,
                          binary=binary, icon_path=icon_path, globs=globs)
        self.register(mt)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')

    @security.protected(ManagePortal)
    def manage_editMimeType(self, name, new_name, mimetypes, extensions,
                            icon_path, binary=0, globs=None, REQUEST=None):
        """Edit a mime type by name
        """
        mt = self.lookup(name)[0]
        self.unregister(mt)
        mt.edit(new_name, mimetypes, extensions, icon_path=icon_path,
                binary=binary, globs=globs)
        self.register(mt)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url() + '/manage_main')


InitializeClass(MimeTypesRegistry)
registerToolInterface('mimetypes_registry', IMimetypesRegistryTool)


def split(name):
    """ split a mime type in a (major / minor) 2-uple """
    try:
        major, minor = name.split('/', 1)
    except:
        raise MimeTypeException('Malformed MIME type (%s)' % name)
    return major, minor
