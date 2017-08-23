"""Interfaces for the unique id utility.
"""
from zope.interface import Interface, Attribute, implementer

class IntIdMissingError(KeyError):
    """
    Raised when ``getId`` cannot find an intid.
    """

class ObjectMissingError(KeyError):
    """
    Raised when ``getObject`` cannot find an object.
    """

class IntIdsCorruptedError(KeyError):
    """
    Raised when internal corruption is detected in the utility.

    Users should not need to catch this because this situation should
    not happen.
    """

class IIntIdsQuery(Interface):
    "Query for IDs and objects"

    def getObject(uid):
        """Return an object by its unique id"""

    def getId(ob):
        """Get a unique id of an object.
        """

    def queryObject(uid, default=None):
        """Return an object by its unique id

        Return the default if the uid isn't registered
        """

    def queryId(ob, default=None):
        """Get a unique id of an object.

        Return the default if the object isn't registered
        """

    def __iter__():
        """Return an iteration on the ids"""


class IIntIdsSet(Interface):
    "Register and unregister objects."

    def register(ob):
        """Register an object and returns a unique id generated for it.

        The object *must* be adaptable to :class:`~zope.keyreference.interfaces.IKeyReference`.

        If the object is already registered, its id is returned anyway.
        """

    def unregister(ob):
        """Remove the object from the indexes.

        IntIdMissingError is raised if ob is not registered previously.
        """

class IIntIdsManage(Interface):
    """Some methods used by the view."""

    def __len__():
        """Return the number of objects indexed."""

    def items():
        """Return a list of (id, object) pairs."""


class IIntIds(IIntIdsSet, IIntIdsQuery, IIntIdsManage):
    """A utility that assigns unique ids to objects.

    Allows to query object by id and id by object.
    """


class IIntIdEvent(Interface):
    """Generic base interface for IntId-related events"""

    object = Attribute("The object related to this event")

    original_event = Attribute("The ObjectEvent related to this event")


class IIntIdRemovedEvent(IIntIdEvent):
    """A unique id will be removed

    The event is published before the unique id is removed
    from the utility so that the indexing objects can unindex the object.
    """


@implementer(IIntIdRemovedEvent)
class IntIdRemovedEvent(object):
    """The event which is published before the unique id is removed
    from the utility so that the catalogs can unindex the object.
    """

    def __init__(self, object, event):
        self.object = object
        self.original_event = event


class IIntIdAddedEvent(IIntIdEvent):
    """A unique id has been added

    The event gets sent when an object is registered in a
    unique id utility.
    """

    idmap = Attribute("The dictionary that holds an (utility -> id) mapping of created ids")


@implementer(IIntIdAddedEvent)
class IntIdAddedEvent(object):
    """The event which gets sent when an object is registered in a
    unique id utility.
    """

    def __init__(self, object, event, idmap=None):
        self.object = object
        self.original_event = event
        self.idmap = idmap
