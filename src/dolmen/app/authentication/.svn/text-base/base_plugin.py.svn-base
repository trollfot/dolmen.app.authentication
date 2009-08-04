# -*- coding: utf-8 -*-

import grok
from interfaces import IUser, IAccountStatus
from zope.component import queryUtility
from dolmen.app.authentication import IUserDirectory
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.authentication.interfaces import IAuthenticatorPlugin


def initialize_auth(pau):
    """Initialize an authentication plugin.
    """
    pau.credentialsPlugins = ["No Challenge if Authenticated", "credentials"]
    pau.authenticatorPlugins = ['users']


class MySessionCredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.name('credentials')
    grok.provides(ICredentialsPlugin)

    loginpagename = 'login'
    loginfield = 'login'
    passwordfield = 'password'


class PrincipalInfo(grok.Adapter):
    grok.context(IUser)
    grok.implements(IPrincipalInfo)
    
    def __init__(self, context):
        self.id = context.id
        self.title = context.title
        self.description = context.title
        self.credentialsPlugin = None
        self.authenticatorPlugin = None
        self.context = context


class UserAuthenticatorPlugin(grok.GlobalUtility):
    grok.provides(IAuthenticatorPlugin)
    grok.name('users')

    def getAccount(self, id):
        users = queryUtility(IUserDirectory)
        if not users:
            return
        return users.getUserByLogin(id)

    def authenticateCredentials(self, credentials):
        if (not isinstance(credentials, dict) or
            not ('login' in credentials and 'password' in credentials)):
            return None

        if credentials['login'] in ['zope.Anybody', 'zope.Everybody']:
            return None

        account = self.getAccount(credentials['login'])

        if (account is None or
            not account.checkPassword(credentials['password'])):
            return None

        status = IAccountStatus(account, None)
        if status is not None and not status.check():
            return None
        
        principal = IPrincipalInfo(account)
        return principal

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is None:
            return None
        return IPrincipalInfo(account)
