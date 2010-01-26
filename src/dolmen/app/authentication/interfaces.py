# -*- coding: utf-8 -*-

from dolmen.app.authentication import MF as _
from dolmen.authentication import (
    IPrincipal, IPasswordProtected, IPrincipalFolder)
# BBB
from dolmen.authentication import IPrincipalFolder as IUserDirectory

from z3c.schema.email import RFC822MailAddress
from zope import schema
from zope.interface import invariant
from zope.interface.exceptions import Invalid
from zope.container.constraints import containers


class IChangePassword(IPasswordProtected):
    """This interface defines a convenient way to change a password,
    including a double check.
    """    
    verify_pass = schema.Password(
        title = _(u"Password checking"),
        description = _(u"Retype the password."),
        required = True
        )
    
    @invariant
    def check_pass(data):
        if data.password != data.verify_pass:
            raise Invalid(_(u"Mismatching passwords."))


class IUser(IPrincipal, IPasswordProtected):
    containers(IPrincipalFolder)

    email = RFC822MailAddress(
        title = _(u'Email address'),
        description = _(u'Enter a valid email address.'),
        required = False
        )

