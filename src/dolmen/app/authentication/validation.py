# -*- coding: utf-8 -*-

from zope.schema import ValidationError
from zope.interface import implements
from zope.app.form.interfaces import IWidgetInputError


class UserRegistrationError(ValidationError):
    implements(IWidgetInputError)
