# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component.interfaces import IObjectEvent, ObjectEvent


class IUserLoggedInEvent(IObjectEvent):
    """An event trigged when a user logs in.
    """


class IUserLoggedOutEvent(IObjectEvent):
    """An event trigged when a user logs out.
    """


class UserLoginEvent(ObjectEvent):
    """A basic implementation of an IUserLoggedInEvent.
    """
    implements(IUserLoggedInEvent)
    

class UserLogoutEvent(ObjectEvent):
    """A basic implementation of an IUserLoggedOutEvent.
    """
    implements(IUserLoggedOutEvent)
