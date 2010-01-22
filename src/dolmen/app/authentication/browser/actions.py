# -*- coding: utf-8 -*-

import grok
import megrok.menu

from zope.interface import Interface
from dolmen.app.layout import master, MenuViewlet
from dolmen.app.authentication import permissions
from dolmen.app.security.content import CanViewContent
from zope.authentication.interfaces import IUnauthenticatedPrincipal

grok.context(Interface)


class AnonymousActionsMenu(megrok.menu.Menu):
    megrok.menu.name(u'anonymous-actions')
    megrok.menu.title(u'Anonymous actions bar')


class AnonymousMenuEntry(object):
    grok.baseclass()
    megrok.menu.menuitem(AnonymousActionsMenu)
    grok.require(permissions.CanLogin)


class UserActionsMenu(megrok.menu.Menu):
    megrok.menu.name(u'user-actions')
    megrok.menu.title(u'User actions bar')

 
class UserMenuEntry(object):
    grok.baseclass()
    grok.context(Interface)
    megrok.menu.menuitem(UserActionsMenu)


class ActionBarViewlet(MenuViewlet):
    grok.order(20)
    grok.name('dolmen.actionbar')
    grok.require(CanViewContent)
    grok.viewletmanager(master.Top)

    @property
    def menu_name(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            return "anonymous-actions"
        return "user-actions"
