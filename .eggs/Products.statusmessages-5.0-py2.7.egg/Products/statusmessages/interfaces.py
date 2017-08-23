# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IMessage(Interface):
    """A single status message."""

    message = Attribute('The text of this message. Usally a Message object.')

    type = Attribute('The type of this message.')


class IStatusMessage(Interface):
    """An adapter for the BrowserRequest to handle status messages."""

    def addStatusMessage(text, type=u'info'):
        """Add a status message."""

    def add(text, type=u'info'):
        """Add a status message."""

    def showStatusMessages():
        """Removes all status messages and returns them for display.
        """
    def show():
        """Removes all status messages and returns them for display.
        """
