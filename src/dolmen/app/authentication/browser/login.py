#!/usr/bin/python
# -*- coding: utf-8 -*-

import grok
import megrok.menu
import zope.schema
import zope.interface
import megrok.z3cform.base as z3cform

from zope.event import notify
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from dolmen.app.layout import Form
from dolmen.app.authentication import events
from dolmen.app.authentication import IUserDirectory
from dolmen.app.authentication.browser import UserAnonymousMenu

_ = MessageFactory('dolmen_authentication')


class ILoginForm(zope.interface.Interface):
    """A simple login form interface.
    """
    login = zope.schema.TextLine(
        title = _(u"Username"),
        )
    
    password = zope.schema.Password(
        title = _(u"Password"),
        )


class Login(Form):
    """A very basic implementation of a login form.
    """
    grok.title(_(u"Log in"))
    grok.require('zope.Public')
    grok.context(zope.interface.Interface)
    megrok.menu.menuitem(UserAnonymousMenu)

    prefix = ""
    label = _(u"Identify yourself")
    form_name = _(u"Login form")
    fields = z3cform.field.Fields(ILoginForm)

    def updateWidgets(self):
        Form.updateWidgets(self)
        self.widgets.prefix = ''
        self.widgets.update()

    @z3cform.button.buttonAndHandler(_('Log in'), name='login')
    def login(self, data):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.status = _(u"Login failed")
        else:
            notify(events.UserLoginEvent(self.request.principal))
            camefrom = self.request.get('camefrom', None)
            if not camefrom:
                directory = getUtility(IUserDirectory)
                user = directory.getUserByLogin(self.request.principal.id)
                camefrom = absoluteURL(user, self.request)
            self.redirect(camefrom)
