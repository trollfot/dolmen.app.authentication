# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.pluggableauth.interfaces import ICredentialsPlugin
from wc.cookiecredentials.plugin import CookieCredentialsPlugin


class CookiesCredentials(grok.GlobalUtility, CookieCredentialsPlugin):
    grok.name('cookies')
    grok.provides(ICredentialsPlugin)

    loginpagename = 'login'
    loginfield = 'login'
    passwordfield = 'password'
