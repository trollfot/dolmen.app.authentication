import grok
from zope.authentication.interfaces import IAuthentication
from zope.component import getUtility
from zope.interface import Interface
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import ITraversable
from zope.location import LocationProxy
from grok.interfaces import IApplication
from dolmen.app.layout import Index, Page, ContextualMenuEntry


class AuthManagement(grok.MultiAdapter):
    grok.name('users')
    grok.provides(ITraversable)
    grok.adapts(IApplication, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        pau = getUtility(IAuthentication)
        return LocationProxy(pau, self.context, "++users++")


class PAUIndex(Index):
    grok.context(IAuthentication)
    
    def render(self):
        return u"Authentication management"


class PAUPrincipalFolder(Page, ContextualMenuEntry):
    grok.title("Directories and users")
    grok.context(IAuthentication)
    
    def render(self):
        u""
