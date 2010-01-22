# -*- coding: utf-8 -*-

import grok
from dolmen.app.authentication import IUserDirectory
from dolmen.app.authentication import IAccountStatus, IPasswordChecker

from zope.component import queryUtility
from zope.principalregistry.principalregistry import principalRegistry
from zope.app.authentication import interfaces as auth
from zope.app.authentication.principalfolder import PrincipalInfo
from zope.app.authentication.httpplugins import HTTPBasicAuthCredentialsPlugin
from wc.cookiecredentials.plugin import CookieCredentialsPlugin


def initialize_pau(PAU):
    """Initialize an authentication plugin.
    """
    PAU.authenticatorPlugins = ['userdirectory', "principalregistry"]
    PAU.credentialsPlugins = ["credentials", "No Challenge if Authenticated"]


class MySessionCredentialsPlugin(grok.GlobalUtility, CookieCredentialsPlugin):
    grok.name('credentials')
    grok.provides(auth.ICredentialsPlugin)

    loginpagename = 'login'
    loginfield = 'login'
    passwordfield = 'password'


class PrincipalRegistryAuthenticator(grok.GlobalUtility):
    """An authenticator plugin, that authenticates principals against
    the global principal registry.

    This authenticator does not support own prefixes, because the
    prefix of its principals is already defined in another place
    (site.zcml). Therefore we get and give back IDs as they are.
    """
    grok.name('principalregistry')
    grok.provides(auth.IAuthenticatorPlugin)

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        principal = None
        login, password = credentials['login'], credentials['password']
        try:
            principal = principalRegistry.getPrincipalByLogin(login)
        except KeyError:
            return
        if principal and principal.validate(password):
            print principal.id
            return PrincipalInfo(unicode(principal.id),
                                 principal.getLogin(),
                                 principal.title,
                                 principal.description)
        return

    def principalInfo(self, id):
        principal = principalRegistry.getPrincipal(id)
        if principal is not None:
            return PrincipalInfo(unicode(principal.id),
                                 principal.getLogin(),
                                 principal.title,
                                 principal.description)


class UserAuthenticatorPlugin(grok.GlobalUtility):
    grok.provides(auth.IAuthenticatorPlugin)
    grok.name('userdirectory')

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
