# -*- coding: utf-8 -*-

import grok

from zope.event import notify
from zope.traversing.browser import AbsoluteURL
from zope.component import getMultiAdapter, getUtility
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import IAuthentication, ILogout

from dolmen.app.layout import Page
from dolmen.app.site import IDolmen
from dolmen.app.authentication import events, mf as _
from dolmen.app.authentication.browser import UserMenuEntry


class LogoutAction(grok.View, UserMenuEntry):
    grok.title(_(u'Log out'))
    grok.template('logout')
    grok.require('zope.View')

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            notify(events.UserLogoutEvent(self.request.principal))
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(self.request)
        self.goto = self.application_url() + '/logout.html'


class LoggedOut(Page):
    grok.name('logout.html')
    grok.require("zope.Public")
    grok.context(IDolmen)
