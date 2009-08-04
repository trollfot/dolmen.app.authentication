# -*- coding: utf-8 -*-

import grok
import megrok.menu
from dolmen.app.site import IDolmen
from dolmen.app.layout import master, Page
from dolmen.app.authentication import events

from zope.event import notify
from zope.interface import Interface
from zope.traversing.browser import AbsoluteURL
from zope.component import getMultiAdapter, getUtility
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import IAuthentication, ILogout
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.i18nmessageid import MessageFactory
    
_ = MessageFactory("dolmen_authentication")
grok.templatedir('templates')
grok.context(Interface)


class UserAnonymousMenu(megrok.menu.Menu):
    megrok.menu.name(u'user_anonymous')
    megrok.menu.title(u'Login and user actions')


class UserAuthenticatedMenu(megrok.menu.Menu):
    megrok.menu.name(u'user_authenticated')
    megrok.menu.title(u'Login and user actions')
    

class AuthenticationBar(grok.Viewlet):
    grok.name('dolmen.authentication')
    grok.viewletmanager(master.DolmenTop)
    grok.order(20)
    grok.template('menu')


    def _authenticated(self):
        menu = getUtility(IBrowserMenu, u'user_authenticated')
        return menu.getMenuItems(self.context, self.request)


    def _anonymous(self):
        menu = getUtility(IBrowserMenu, u'user_anonymous')
        return menu.getMenuItems(self.context, self.request)

        
    def update(self):
        self.anonymous = IUnauthenticatedPrincipal.providedBy(
            self.request.principal
            )
        self.contexturl = AbsoluteURL(self.context, self.request)

        if not self.anonymous:
            self.principal = self.request.principal.title
            self.actions = self._authenticated()
        else:
            self.actions = self._anonymous()


class LogoutAction(grok.View):
    grok.title(_(u'Log out'))
    grok.template('logout')
    megrok.menu.menuitem(UserAuthenticatedMenu)

    def update(self):
        notify(events.UserLogoutEvent(self.request.principal))
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(self.request)
        self.goto = self.application_url() + '/logout.html'


class LoggedOut(Page):
    grok.name('logout.html')
    grok.require("zope.Public")
    grok.context(IDolmen)
