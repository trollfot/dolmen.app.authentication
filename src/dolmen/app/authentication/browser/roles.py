import grok
from zope import schema
from zope.interface import Interface
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.security.settings import Allow
from zope.site.hooks import getSite

from dolmen.app import layout
from dolmen.app.authentication import IUser
from dolmen.forms.base import Fields


class IRoleGranting(Interface):
    roles = schema.List(
        value_type=schema.Choice(vocabulary='Role Ids'),
        required=True
        )


class UserGranting(grok.Adapter):
    grok.implements(IRoleGranting)
    grok.context(IUser)

    def __init__(self, context):
        self.context = context
        site = getSite()
        self.rolemap = IPrincipalRoleMap(site)
        self.manager = IPrincipalRoleManager(site)
        self.setting = self.rolemap.getRolesForPrincipal(self.context.id)

    def get_roles(self):
        return [role[0] for role in self.setting if
                self.rolemap.getSetting(role[0], self.context.id) is Allow]

    def set_roles(self, roles):
        userid = self.context.id

        # removing undefined roles
        for role in self.setting:
            if role[0] not in roles:
                setting = self.rolemap.getSetting(role[0], userid)
                if setting is Allow:
                    self.manager.unsetRoleForPrincipal(role[0], userid)

        # setting new roles
        for role in roles:
            self.manager.assignRoleToPrincipal(role, userid)

    roles = property(get_roles, set_roles)


class UserRoles(layout.Edit):
    grok.context(IUser)
    grok.name('grant_role')
    grok.title(u"Grant role")
    grok.require("dolmen.security.ManageUsers")

    form_name = u"Select user's roles"
    fields = Fields(IRoleGranting)
