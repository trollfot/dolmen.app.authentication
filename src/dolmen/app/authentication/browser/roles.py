import grok
from zope import schema
from zope.interface import Interface
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.settings import Allow
from zope.site.hooks import getSite

from dolmen.app import layout
from dolmen.app.authentication import IUser
from dolmen.app.authentication import permissions
from dolmen.app.authentication import MF as _
from dolmen.forms.base import Fields


class IUserRoles(Interface):
    """Defines a component allowing you to chose roles.
    """
    roles = schema.List(
        value_type=schema.Choice(vocabulary='Role Ids'),
        required=True)


class UserRoles(grok.Adapter):
    """Grant a role to a user.
    """
    grok.context(IUser)
    grok.implements(IUserRoles)

    def __init__(self, context):
        self.context = context
        site = getSite()
        self.manager = IPrincipalRoleManager(site)
        self.setting = self.manager.getRolesForPrincipal(self.context.id)

    @apply
    def roles():
        def get(self):
            return [role[0] for role in self.setting if role[1] is Allow]

        def set(self, roles):
            userid = self.context.id

            # removing undefined roles
            for role in self.setting:
                if role[0] not in roles:
                    if role[1] is Allow:
                        self.manager.unsetRoleForPrincipal(role[0], userid)

            # setting new roles
            for role in roles:
                self.manager.assignRoleToPrincipal(role, userid)


class EditUserRoles(layout.Edit):
    grok.context(IUser)
    grok.name('grant_role')
    grok.title(_(u"Grant role"))
    grok.require(permissions.ManageUsers)

    form_name = _(u"Select user's roles")
    fields = Fields(IUserRoles)
