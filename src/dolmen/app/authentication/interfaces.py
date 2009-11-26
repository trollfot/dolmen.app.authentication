# -*- coding: utf-8 -*-

from zope import schema
import dolmen.content as dolmen
import zope.security.interfaces
from z3c.schema.email import RFC822MailAddress
from zope.i18nmessageid import MessageFactory
from zope.interface.exceptions import Invalid
from zope.interface import Interface, Attribute, invariant
from zope.container.constraints import contains, containers

_ = MessageFactory('dolmen_authentication')


class IUserDirectory(Interface):
    contains('.IPrincipal')
    
    def getIdByLogin(login):
        """Returns the principal's id with the given login.
        """

    def getUserByLogin(login):
        """Returns the principal object with the given login.
        """


class IPasswordProtected(Interface):
    """This interface defines items protected by a password.
    """
    password = schema.Password(
        title = _(u"Password"),
        description = _(u"Enter a password"),
        required = True
        )


class IPasswordChecker(Interface):
    """This interface defines items that can challenge a
    given value against a stored password value.
    """
    def checkPassword(password):
        """Challenges the input password with the stored one.
        Returns True if the passwords match, False otherwise.
        """


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


        
class IPrincipal(zope.security.interfaces.IGroupAwarePrincipal):
    """Principals are easily identifiable entities that interact
    with the content. Commonly, a principal is a user or a group.
    """
    id = schema.ASCIILine(
        title = _(u'Login'),
        required = True
        )

    title = schema.TextLine(
        title = _(u'Full name'),
        description = _(u'Enter your full name.'),
        required = True,
        )

    email = RFC822MailAddress(
        title = _(u'Email address'),
        description = _(u'Enter a valid email address.'),
        required = False
        )


class IUser(IPrincipal, IPasswordProtected):
    containers(IUserDirectory)
    

class IGroup(IPrincipal):
    pass


class IAccountStatus(Interface):
    """An interface managing a simple account status.
    """
    status = Attribute("Status of the account.")
    
    def check():
        """Returns a boolean. True allows the normal user login.
        False will disable the account and act like a failed login.
        """
