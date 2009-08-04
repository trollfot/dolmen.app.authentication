import grok
from grok import index
from dolmen.app.site import IDolmen
from zope.security.interfaces import IPrincipal
from dolmen.app.authentication.interfaces import IUser


class UserIndexes(grok.Indexes):
    grok.site(IDolmen)
    grok.context(IUser)

    fullname = index.Text(attribute='title')


class PrincipalIndexes(grok.Indexes):
    grok.site(IDolmen)
    grok.context(IPrincipal)

    id = index.Field()
