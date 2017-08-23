# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.mime_types import smi_mimetypes

import logging


logger = logging.getLogger(__name__)


def fixUpSMIGlobs(context, reinit=True):
    # This method is used both in migrations where we need the reinit and
    # during site creation, where the registry has already been initialized.
    mtr = getToolByName(context, 'mimetypes_registry')
    if reinit:
        smi_mimetypes.initialize(mtr)

    # Now comes the fun part. For every glob, lookup a extension
    # matching the glob and unregister it.
    for glob in mtr.globs.keys():
        if glob not in mtr.extensions:
            continue
        logger.debug(
            'Found glob %s in extensions registry, removing.' % glob
        )
        mti = mtr.extensions[glob]
        del mtr.extensions[glob]
        if glob in mti.extensions:
            logger.debug('Found glob %s in mimetype %s extensions, '
                         'removing.' % (glob, mti))
            exts = list(mti.extensions)
            exts.remove(glob)
            mti.extensions = tuple(exts)
            mtr.register(mti)


def post_install(context):
    fixUpSMIGlobs(context, reinit=False)
