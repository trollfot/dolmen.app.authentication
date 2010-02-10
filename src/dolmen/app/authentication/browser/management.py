import grok
from zope.schema import Tuple, Choice, ASCIILine
from zope.authentication.interfaces import IAuthentication
from dolmen.authentication import IPrincipalFolder
from zope.component import getUtility
from zope.interface import Interface
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import ITraversable
from zope.location import LocationProxy
from grok.interfaces import IApplication
from dolmen.app.layout import Index, Page, ContextualMenuEntry, Edit
from dolmen.forms.base import Fields

from zope import interface
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory, ISource


class PrincipalFoldersList(grok.GlobalUtility):
    grok.name('dolmen.PAUPrincipalFolders')
    grok.provides(IVocabularyFactory)
    interface.implements(ISource)

    def __call__(self, pau):
        return SimpleVocabulary(
            [SimpleTerm(value=p.__name__, token=p.__name__, title=p.title)
             for p in pau.values() if IPrincipalFolder.providedBy(p)])


class IActiveFolders(Interface):
    """Principal folders management.
    """   
    activeFolders = Tuple(
        title=u"Active user folders",
        value_type=Choice(vocabulary='dolmen.PAUPrincipalFolders'),
        default=tuple())


class ActiveFoldersChoice(grok.Adapter):
    grok.implements(IActiveFolders)
    grok.context(IAuthentication)

    @property
    def activeFolders(self):
        return tuple((p for p in self.context.authenticatorPlugins
                      if IPrincipalFolder.providedBy(self.context.get(p))))

    @activeFolders.setter
    def activeFolders(self, values):
        auths = set(self.context.authenticatorPlugins)
        folders = set((p.__name__ for p in self.context.values()
                       if IPrincipalFolder.providedBy(p)))

        self.context.authenticatorPlugins = (
            tuple(auths.difference(folders)) + values)


class PAUIndex(Index):
    grok.context(IAuthentication)
    
    def render(self):
        return u"Authentication management"


class PAUPrincipalFolder(Page, ContextualMenuEntry):
    grok.title("User folders")
    grok.context(IAuthentication)
    
    def render(self):
        return self.context.authenticatorPlugins


class PAUPreferences(Edit):
    grok.name('preferences')
    grok.context(IAuthentication)
    fields = Fields(IActiveFolders)
    label = u"Preferences"
