#!/usr/bin/python
# -*- coding: utf-8 -*-

import grok

from dolmen.app.authentication import ManageUsers
from dolmen.app.layout import Index, Page, ContextualMenuEntry, Edit
from dolmen.authentication import IPrincipalFolder
from dolmen.forms.base import Fields
from grok.interfaces import IApplication

from zope.authentication.interfaces import IAuthentication
from zope.component import getUtility
from zope.interface import Interface
from zope.location import LocationProxy
from zope.publisher.interfaces.http import IHTTPRequest
from zope.schema import Tuple, Choice, ASCIILine
from zope.schema.interfaces import IVocabularyFactory, ISource
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.interfaces import ITraversable


class PrincipalFoldersList(grok.GlobalUtility):
    grok.name('dolmen.PAUPrincipalFolders')
    grok.implements(ISource)
    grok.provides(IVocabularyFactory)

    def __call__(self, pau):
        return SimpleVocabulary(
            [SimpleTerm(value=p.__name__, token=p.__name__,
                        title="%s (%s)" % (p.__name__, p.title or p.__name__))
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

    @apply
    def activeFolders():
        """Property allowing to access and set the active
        PrincipalFolders of the adapted PAU.
        """
        def fget(self):
            return tuple(
                (p for p in self.context.authenticatorPlugins
                 if IPrincipalFolder.providedBy(self.context.get(p))))

        def fset(self, values):
            auths = set(self.context.authenticatorPlugins)
            folders = set(
                (p.__name__ for p in self.context.values()
                 if IPrincipalFolder.providedBy(p)))
            
            self.context.authenticatorPlugins = (
                tuple(auths.difference(folders)) + values)

        return property(fget, fset)


class ManageAuth(Index):
    grok.context(IAuthentication)
    grok.require(ManageUsers)


class PrincipalFolders(Page, ContextualMenuEntry):
    grok.title("User folders")
    grok.context(IAuthentication)
    grok.require(ManageUsers)
    
    def update(self):
        self.folders = self.context.authenticatorPlugins
        self.credentials = self.context.credentialsPlugins


class PAUPreferences(Edit):
    grok.name('authenticators')
    grok.context(IAuthentication)
    grok.require(ManageUsers)
    
    fields = Fields(IActiveFolders)
    label = u"Manage your authentication sources"
