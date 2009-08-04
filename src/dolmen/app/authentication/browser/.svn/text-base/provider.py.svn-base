# -*- coding: utf-8 -*-

from zope.interface import Interface
from grok.interfaces import IGrokView
from zope.schema import TextLine, Int, List
import grok


class IUsersListing(IGrokView):
    """A view listing users.
    """
    users = List(
        title = u"Users",
        description = u"A list of IUsers",
        required = True
        )

    search = TextLine(
        title = u"Search term",
        description = u"A complete or partial username to filter on.",
        required = False,
        )

    limit = Int(
        title = u"Limit",
        description = u"Users batch size (0 equals no batching)",
        default = 0,
        )


class UsersProvider(grok.ViewletManager):
    grok.view(IUsersListing)
    grok.name(u"dolmen.users")
    grok.context(Interface)
