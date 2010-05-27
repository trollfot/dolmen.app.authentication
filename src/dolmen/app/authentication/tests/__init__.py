# Test package.

import grok
from dolmen.app.site import Dolmen
from zope.authentication.interfaces import IAuthentication
from zope.pluggableauth import PluggableAuthentication as PAU
from dolmen.app.authentication import initialize_pau


class MySite(Dolmen):
    grok.local_utility(PAU, IAuthentication, setup=initialize_pau,
                       public=True, name_in_container="users")
