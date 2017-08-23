# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from Products.statusmessages.interfaces import IMessage
from zope.interface import implementer

import struct


def _utf8(value):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    elif isinstance(value, str):
        return value
    return ''


def _unicode(value):
    return unicode(value, 'utf-8', 'ignore')


@implementer(IMessage)
class Message:
    """A single status message.

    Let's make sure that this implementation actually fulfills the
    'IMessage' API.

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(IMessage, Message)
      True

      >>> status = Message(u'this is a test', type=u'info')
      >>> status.message == 'this is a test'
      True

      >>> status.type == 'info'
      True

    It is quite common to use MessageID's as status messages:

      >>> from zope.i18nmessageid import MessageFactory
      >>> from zope.i18nmessageid import Message as I18NMessage
      >>> msg_factory = MessageFactory('test')

      >>> msg = msg_factory(u'test_message', default=u'Default text')

      >>> status = Message(msg, type=u'warn')
      >>> status.type == 'warn'
      True

      >>> type(status.message) is I18NMessage
      True

      >>> status.message.default == 'Default text'
      True

      >>> status.message.domain == u'test'
      True

    """

    def __init__(self, message, type=''):
        self.message = message
        self.type = type

    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        if self.message == other.message and self.type == other.type:
            return True
        return False

    def encode(self):
        """
        Encode to a cookie friendly format.

        The format consists of a two bytes length header of 11 bits for the
        message length and 5 bits for the type length followed by two values.
        """
        message = _utf8(self.message)[:0x3FF]  # we can store 2^11 bytes
        type = _utf8(self.type)[:0x1F]         # we can store 2^5 bytes
        size = (len(message) << 5) + (len(type) & 31)  # pack into 16 bits

        return struct.pack(
            '!H{0}s{1}s'.format(len(message), len(type)),
            size,
            message,
            type,
        )


def decode(value):
    """
    Decode messages from a cookie

    We return the decoded message object, and the remainder of the cookie
    value (it can contain further messages).

    We expect at least 2 bytes (size information).
    """
    if len(value) >= 2:
        size = struct.unpack('!H', value[:2])[0]
        msize, tsize = (size >> 5, size & 31)
        message = Message(
            _unicode(value[2:msize+2]),
            _unicode(value[msize+2:msize+tsize+2]),
        )
        return message, value[msize+tsize+2:]
    return None, ''
