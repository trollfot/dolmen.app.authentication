# -*- coding: utf-8 -*-

import grokcore.component as grok
from dolmen.app.authentication import IUser
from zope.app.authentication.interfaces import IPrincipalInfo


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
