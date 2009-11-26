# -*- coding: utf-8 -*-

import grok
from dolmen.app.authentication import IUserDirectory
from dolmen.app.authentication import IAccountStatus, IPasswordChecker

from zope.component import queryUtility
from zope.app.authentication import interfaces as auth
from wc.cookiecredentials.plugin import CookieCredentialsPlugin


def initialize_pau(PAU):
    """Initialize an authentication plugin.
    """
    PAU.credentialsPlugins = ["No Challenge if Authenticated", "credentials"]
    PAU.authenticatorPlugins = ['users']


class MySessionCredentialsPlugin(grok.GlobalUtility, CookieCredentialsPlugin):
    grok.name('credentials')
    grok.provides(auth.ICredentialsPlugin)

    loginpagename = 'login'
    loginfield = 'login'
    passwordfield = 'password'


class UserAuthenticatorPlugin(grok.GlobalUtility):
    grok.provides(auth.IAuthenticatorPlugin)
    grok.name('users')

    def getAccount(self, id):
        users = queryUtility(IUserDirectory)
        if not users:
            return
        return users.getUserByLogin(id)


    def getValidPrincipal(self, login, passwd):
        """Retrives a principal account and returns a IPrincipalInfo object.
        If no user matches the login or if the password check doesn't work,
        None is returned instead.
        """
        # Retrieving the user
        account = self.getAccount(login)
        if account is None:
            return None

        # Checking the status of the account
        status = IAccountStatus(account, None)
        if status is not None and not status.check():
            return None

        # Checking credentials.
        checker = IPasswordChecker(account)
        if checker.checkPassword(passwd) is not True:
            return None

        return auth.IPrincipalInfo(account)


    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None

        login = credentials.get('login')
        passwd = credentials.get('password')
        if not login or not passwd:
            return None

        # We do not check the validity for known core users.
        if login in ['zope.Anybody', 'zope.Everybody']:
            return None

        return self.getValidPrincipal(login, passwd)


    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is not None:
            return auth.IPrincipalInfo(account)
        return None
