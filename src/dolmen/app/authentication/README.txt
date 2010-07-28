*************************
dolmen.app.authentication
*************************

``dolmen.app.authentication`` is the package responsible for the users and
groups management in a Dolmen application. Built on the on the top of
``dolmen.authentication`` and ``zope.pluggableauth``, it provides a
set of plugins and base classes that can help building a complex users
& groups system.

Initial Grok imports
====================

  >>> import grok
  >>> from grokcore.component.testing import grok_component


Credentials plugins
===================

  >>> from zope.pluggableauth.interfaces import ICredentialsPlugin

Credentials plugins are responsible for the extraction of credentials,
in order to identify a user. ``dolmen.app.authentication`` provides a
single plugin, out of the box - Cookies Credentials.

Cookies Credentials
-------------------

The cookie credentials plugin extracts the credentials from cookies.
This plugin is based on Philipp von Weitershausen's work
(``wc.cookiecredentials``). It has been reimplemented to avoid the use
of the ``zope.app`` packages and allow more flexibility in the long run.

This plugin provides the following capabilities:

- challenge the user to enter username and password through a login
  form;

- save those credentials to a cookie from which it can read them back
  at any later time.

To check if the credentials can correctly be exacted, we can forge the
cookie ourselves in a test request::

  >>> import base64
  >>> from zope.publisher.browser import TestRequest

  >>> cookie = base64.encodestring('mgr:mgrpw')
  >>> request = TestRequest()
  >>> request._cookies = {'dolmen.authcookie': cookie}

Calling the plugin credentials extractor will give us exactly what we
need to proceed to the authentication::

  >>> from zope.interface.verify import verifyObject
  >>> from dolmen.app.authentication.plugins import CookiesCredentials

  >>> plugin = CookiesCredentials()
  >>> verifyObject(ICredentialsPlugin, plugin)
  True

  >>> print plugin.extractCredentials(request)
  {'login': 'mgr', 'password': 'mgrpw'}


Authenticator Plugins
=====================

  >>> from zope.pluggableauth.interfaces import IAuthenticatorPlugin

Authenticator plugins uses extracted credentials in order to retrieve
and identify principals. ``dolmen.app.authentication`` provides two
plugins - Global Registry Authentication & Principal Folder Authentication


Global Registry Authentication
------------------------------

In order to register principals, the ``zope.principalregistry``
package provides a global registry that is not persistent and
re-constructed at each startup. The Global Registry Authenticator is
meant to look up the principal inside that global registry.

We verify the integrity of our implementation against the
requirements::

  >>> from dolmen.app.authentication import plugins
  >>> IAuthenticatorPlugin.implementedBy(plugins.GlobalRegistryAuth)
  True

  >>> plugin = plugins.GlobalRegistryAuth()
  >>> verifyObject(IAuthenticatorPlugin, plugin)
  True

In order to test this plugin, we registered a user, called "mgr" in
the global registry. We'll test the look up using "mgr" credentials::

  >>> user = plugin.authenticateCredentials(
  ...            {'login': "mgr", "password": "mgrpw"})
  >>> print user
  PrincipalInfo(u'zope.mgr')

Wrong credentials will make the authentication return None::

   >>> user = plugin.authenticateCredentials(
   ...            {'login': "mgr", "password": "wrongpass"})
   >>> user is None
   True

   >>> user = plugin.authenticateCredentials(
   ...            {'login': "anon", "password": "wrongpass"})
   >>> user is None
   True

It is possible to get the principal info alone, as required by the
IAuthenticatorPlugin interface::

   >>> print plugin.principalInfo('zope.mgr')
   PrincipalInfo(u'zope.mgr')

   >>> print plugin.principalInfo('zorglub')
   None

Note that the principal info is retrieved using its id and not its
login. The id is unique and prefixed by the registry's own prefix, to
make it easily identifiable and retrievable.


Principal Folder Authentication
-------------------------------

``dolmen.app.authentication`` introduces another authenticator plugin
meant to store and retrieve persistent principals. This plugin is a
container that can store IPrincipal objects and retrieve them
following the IAuthenticatorPlugin's prescriptions.

We verify the integrity of our implementation against the
requirements::

  >>> from dolmen.app.authentication import plugins
  >>> IAuthenticatorPlugin.implementedBy(plugins.PrincipalFolderPlugin)
  True

  >>> plugin = plugins.PrincipalFolderPlugin()
  >>> verifyObject(IAuthenticatorPlugin, plugin)
  True

In order to test this plugin, we have to create an IPrincipal object
and store it inside the plugin. Then, we can test the look up.

In order to make the authentication pluggable, the principal
authenticator plugin relies on 3 interfaces: 

- IAccountStatus : if an adaptation exist to this interface from the
  IPrincipal object, it is used to figure out if the principal can
  login or not. It allows disabling a user account and computing that 
  disability.

- IPasswordChecker: this adapter is used to check the credentials. If
  it doesnt exist (or if the IPrincipal object doesn't provide this
  interface), the authentication is aborted and None is returned.

- IPrincipalInfo: unlike the previous plugin, the Principal Folder
  authenticator doesn't directly return a PrincipalInfo object, but
  uses an adapter to retrieve the appropriate principal info
  object. This is required in order to plug specific behavior into our
  authentication system.


Let's first implement a basic IPrincipalObject. Once stored, we'll be
able to start the look ups and the adapters implementations::

  >>> from dolmen.app.authentication.tests import User

See the implementation below::

  from dolmen.authentication import IPrincipal
  from zope.interface import implements

  class User(object):
      implements(IPrincipal)

      def __init__(self, id, title=u"", desc=u""):
          self.id = id
          self.title = title or id
          self.description = desc
          self.groups = []

We can verify our implementation against the interface::

  >>> from dolmen.authentication import IPrincipal
  >>> stilgar = User(u"stilgar")
  >>> verifyObject(IPrincipal, stilgar)
  True

The implementation is consistent. We can now persist the principal in
the plugin container::

  >>> plugin['stilgar'] = stilgar
  >>> print [user for user in plugin.keys()]
  [u'stilgar']

We can now try to look up the principal, using the authentication API::

  >>> found = plugin.authenticateCredentials(
  ...            {'login': 'stilgar', 'password': 'boo'})
  >>> found is None
  True

The principal is not found : we do not have an adapter to
IPasswordChecker available, therefore the authentication process has
been aborted.

Providing the adapter will allow us to successfully retrieve the
principal::

  >>> from dolmen.authentication import IPasswordChecker

  >>> class GrantingAccessOnBoo(grok.Adapter):
  ...     grok.context(IPrincipal)
  ...     grok.provides(IPasswordChecker)
  ...
  ...     def checkPassword(self, pwd):
  ...         if pwd == 'boo':
  ...             return True

  >>> grok_component('booing', GrantingAccessOnBoo)
  True
 
  >>> found = plugin.authenticateCredentials(
  ...            {'login': 'stilgar', 'password': 'boo'})
  >>> found is not None
  True


Of course, providing a wrong password will return None::

  >>> found = plugin.authenticateCredentials(
  ...            {'login': 'stilgar', 'password': 'not boo'})
  >>> found is None
  True

We can also lookup the principal with its id::

  >>> print plugin.principalInfo('stilgar')
  <dolmen.authentication.principal.LocatablePrincipalInfo ...>

  >>> print plugin.principalInfo("unknown")
  None

As seen previously, it is possible to switch on and off the ability to
log in, for a given user, thanks to the IAccountStatus interface::

  >>> from dolmen.authentication import IAccountStatus

  >>> class AllowLogin(grok.Adapter):
  ...     grok.context(IPrincipal)
  ...     grok.provides(IAccountStatus)
  ...    
  ...     @property
  ...     def status(self):
  ...         return "No status information available"
  ...
  ...     def check(self):
  ...         if self.context.id != "stilgar":
  ...             return True
  ...         return False

  >>> grok_component('allow', AllowLogin)
  True

In this example, we explictly disallow the user with the identifier
"stilgar" to be retrieved by the login::

  >>> found = plugin.authenticateCredentials(
  ...            {'login': 'stilgar', 'password': 'boo'})
  >>> found is None
  True


Setting up a site
=================

In order to test the advanced features of the package, we'll set up a
familiar environment. Doing so, we can test the behavior of our
package in the context of a real Dolmen site::

  >>> from dolmen.app.site import Dolmen
  >>> root = getRootFolder()

  >>> site = Dolmen()
  >>> grok.notify(grok.ObjectCreatedEvent(site))
  >>> root['site'] =  site

  >>> from zope.authentication.interfaces import IAuthentication
  >>> from zope.pluggableauth import PluggableAuthentication
  >>> from dolmen.app.authentication import initialize_pau

  >>> PAU = PluggableAuthentication()
  >>> len(PAU.authenticatorPlugins)
  0
  >>> len(PAU.credentialsPlugins)
  0

  >>> initialize_pau(PAU)
  >>> print PAU.authenticatorPlugins
  ('globalregistry',)
  >>> print PAU.credentialsPlugins
  ('cookies', 'No Challenge if Authenticated')

  >>> site['auth'] = PAU
  >>> lsm = site.getSiteManager()
  >>> lsm.registerUtility(PAU, IAuthentication)


Logging in
==========

UnAuthorized
------------

Imagine you go to a page that anonymous users don't have access to::

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()

  >>> browser.open("http://localhost/site/@@edit")
  >>> unauthorized = browser.contents
  >>> 'id="login" name="login"' in unauthorized
  True
  >>> 'id="password" name="password"' in unauthorized
  True


The login page
--------------

To get the right credentials, we can simply log in, using the login
form provided by ``dolmen.app.authentication``::

  >>> browser.open('http://localhost/site/@@login')
  >>> loginpage = browser.contents
  >>> 'id="login" name="login"' in loginpage
  True
  >>> 'id="password" name="password"' in loginpage
  True

  >>> browser.getControl('Username').value = 'mgr'
  >>> browser.getControl('Password').value = 'mgrpw'
  >>> browser.getControl('Log in').click()

  >>> browser.url
  'http://localhost/site'

  >>> browser.open("http://localhost/site/@@edit")
  >>> "<h1>Edit: My Dolmen Site</h1>\n" in browser.contents
  True


Managing the authentication plugins
====================================

``dolmen.app.authentication`` provides a way to enable and disable the
different authentication plugins.

In order to keep the elements tidied up, in the site,
``dolmen.app.authentication`` assumes that the authenticator plugins
are persisted inside the PAU container.

Let's have a concrete exemple with a PrincipalFolder plugin::

  >>> members = plugins.PrincipalFolderPlugin()
  >>> grok.notify(grok.ObjectCreatedEvent(members))
  >>> PAU['members'] = members

At this point, the PrincipalFolder is created and persisted. As we
notice, the folder is created inside the PAU utility container.

At this point, we can access the management view::

  >>> browser.open("http://localhost/site/auth/@@authenticators")
  >>> print browser.contents
  <!DOCTYPE html PUBLIC...
  <div class="fields">
    <div class="field">
      <label class="field-label"
             for="form-field-activeFolders">Active authentication sources</label>
      ...
      <input type="checkbox" id="form-field-activeFolders-members" name="form.field.activeFolders" value="members" class="field field-tuple" />
      <label for="form-field-activeFolders-members">members (members)</label>
      <br />
      ...

The "members" principal folder is not yet activated.

Let's create a User object inside it::

  >>> chani = User(u"chani", title=u"Sihaya")
  >>> PAU['members']['chani'] = chani

Now, with a new browser, let's try to login::

  >>> new_browser = Browser()
  >>> new_browser.open('http://localhost/site/@@login')
  >>> new_browser.getControl('Username').value = 'chani'
  >>> new_browser.getControl('Password').value = 'boo'
  >>> new_browser.getControl('Log in').click()

  >>> "Login failed" in new_browser.contents
  True

Using the management view mechanisms, we can activate our principal
folder::

  >>> from dolmen.app.authentication.browser import management
  >>> adapter = management.IActiveFolders(PAU)
  >>> adapter.activeFolders
  ()
  >>> adapter.activeFolders = (u'members',)

The principal folder is now activated. Let's retry to log in::

  >>> new_browser = Browser()
  >>> new_browser.handleErrors = False

  >>> new_browser.open('http://localhost/site/@@login')
  >>> new_browser.getControl('Username').value = 'chani'
  >>> new_browser.getControl('Password').value = 'boo'
  >>> new_browser.getControl('Log in').click()

  >>> "Login failed" in new_browser.contents
  False

  >>> print new_browser.url
  http://localhost/site


Managing the users
==================

Users can be granted roles. This can be done through a view, with the
user as the context::

  >>> browser.open("http://localhost/site/auth/members/chani/@@grant_roles")
  >>> print browser.contents
  <!DOCTYPE html PUBLIC...
  ...<h1>Edit: Sihaya</h1>...
  <div class="fields">
    <div class="field">
      <label class="field-label" for="form-field-roles">roles</label>
  ...
      <input type="checkbox" id="form-field-roles-dolmen-Contributor" name="form.field.roles" value="dolmen.Contributor" class="field field-list" />
        <label for="form-field-roles-dolmen-Contributor">dolmen.Contributor</label>
        <br />
       <input type="checkbox" id="form-field-roles-dolmen-Member" name="form.field.roles" value="dolmen.Member" class="field field-list" />
        <label for="form-field-roles-dolmen-Member">dolmen.Member</label>
        <br />
       <input type="checkbox" id="form-field-roles-dolmen-Owner" name="form.field.roles" value="dolmen.Owner" class="field field-list" />
        <label for="form-field-roles-dolmen-Owner">dolmen.Owner</label>
        <br />
       <input type="checkbox" id="form-field-roles-dolmen-Reviewer" name="form.field.roles" value="dolmen.Reviewer" class="field field-list" />
        <label for="form-field-roles-dolmen-Reviewer">dolmen.Reviewer</label>
        <br />
  ...

This view is possible thanks to an adapter, useable on any
IPrincipals::

  >>> from zope.component.hooks import setSite
  >>> setSite(site) # we got to the context of our site

  >>> from dolmen.app.authentication.browser import roles
  >>> role_controller = roles.IPrincipalRoles(chani)
  >>> role_controller.roles
  []

  >>> role_controller.roles = ['dolmen.Member']
  >>> role_controller.roles
  ['dolmen.Member']

The role management applies the changes on the site object
itself. Let's verify if the role has been correctly applied::

  >>> from zope.securitypolicy.interfaces import IPrincipalRoleManager
  >>> prm = IPrincipalRoleManager(site)
  >>> print prm.getRolesForPrincipal(chani.id)
  [('dolmen.Member', PermissionSetting: Allow)]


Logging out
===========

We can also manually destroy the cookie by invoking the logout page::

  >>> 'dolmen.authcookie' in browser.cookies.keys()
  True

  >>> browser.open("http://localhost/site/@@logoutaction")
  >>> 'dolmen.authcookie' in browser.cookies.keys()
  False

  >>> browser.url
  'http://localhost/site/logout.html'
