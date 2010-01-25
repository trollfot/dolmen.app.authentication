# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
MF = MessageFactory('dolmen.app.authentication')

import grok
from dolmen.app.site import IDolmen
from dolmen.app.authentication import plugins
from dolmen.app.authentication.interfaces import IUser, IChangePassword
from dolmen.app.authentication.browser.validation import UserRegistrationError
from grok import index
from zope.security.interfaces import IPrincipal


def initialize_pau(PAU):
    """Initialize an authentication plugin.
    """
    PAU.authenticatorPlugins = ("globalregistry",)
    PAU.credentialsPlugins = ("cookies", "No Challenge if Authenticated")


class UserIndexes(grok.Indexes):
    grok.site(IDolmen)
    grok.context(IPrincipal)

    id = index.Field()
    fullname = index.Text(attribute='title')
