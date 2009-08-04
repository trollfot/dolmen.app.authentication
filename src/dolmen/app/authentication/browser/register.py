# -*- coding: utf-8 -*-

import grok
from zope import schema
from zope.interface import Interface
from dolmen.app.layout import Form
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.principalfolder import InternalPrincipal


class Register(Form):
    grok.context(Interface)
    grok.require("zope.Public")
    form_name = u"Sign up as a portal member"
    
    form_fields = grok.Fields(
        name = schema.TextLine(title=u"Your name"),
        # TODO: validate email address
        email = schema.TextLine(title=u"Email address"),
        password = schema.Password(title=u"Password"),
        password_repeat = schema.Password(title=u"Repeat password"),
        )

    @grok.action('Sign up')
    def sign_up(self, name, email, password, password_repeat):
        # TODO: validate password is equal to password_repeat

        # add principal to principal folder
        pau = component.getUtility(IAuthentication)
        principals = pau['principals']
        principals[email] = user = InternalPrincipal(email, password, name)

        # grant principal the role
        role_manager = IPrincipalRoleManager(self.context)
        role_manager.assignRoleToPrincipal('dolmen.role.Reviewer',
                                           principals.prefix + email)

        self.redirect('index')
