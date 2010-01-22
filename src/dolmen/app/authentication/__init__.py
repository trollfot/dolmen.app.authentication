# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
MF = MessageFactory('dolmen.app.authentication')

from interfaces import IUser, IUserDirectory, IChangePassword
from plugins import initialize_pau
from validation import UserRegistrationError
