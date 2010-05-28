*************************
dolmen.app.authentication
*************************

``dolmen.app.authentication`` is the package responsible for the users
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
single plugin, out of the box.

Cookies Credentials
-------------------

The cookie credentials plugin extracts the credentials from cookies.
This plugin is based on Philipp von Weitershausen's work
(``wc.cookiecredentials``). It has been reimplemented to avoid the use
of the ``zope.app`` packages and allow more flexibility in the
changes, in the long run.

This plugin provides capabilities to::

- challenge the user to enter username and password through a login
  form and

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
plugins.


Global Registry Authentication
------------------------------

In order to register principals, the ``zope.principalregistry``
package provides a global registry that is not persistent and
re-constructed at each startup. The Global Registry Authenticator is
meant to look up the principal inside that global registry.

  >>> from dolmen.app.authentication import plugins
  >>> IAuthenticatorPlugin.implementedBy(plugins.GlobalRegistryAuth)
  True

We verify the integrity of our implementation against the
requirements::

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
IAuthenticatorPlugin interface:

   >>> print plugin.principalInfo('zope.mgr')
   PrincipalInfo(u'zope.mgr')

   >>> print plugin.principalInfo('zorglub')
   Traceback (most recent call last):
   ...   
   PrincipalLookupError: zorglub


Note that the principal info is retrieved using its id and not its
login. The id is unique and prefixed by the registry's own prefix, to
make it easily identifiable and retrievable.


Principal Folder Authentication
-------------------------------

``dolmen.app.authentication`` introduces another authenticator plugin
meant to store and retrieve persistent principals. This plugin is
container that can store IPrincipal objects and retrieve them
following the IAuthenticatorPlugin's prescriptions.

  >>> from dolmen.app.authentication import plugins
  >>> IAuthenticatorPlugin.implementedBy(plugins.PrincipalFolderPlugin)
  True

We verify the integrity of our implementation against the
requirements::

  >>> plugin = plugins.PrincipalFolderPlugin()
  >>> verifyObject(IAuthenticatorPlugin, plugin)
  True

In order to test this plugin, we have to create an IPrincipal object
and to store inside the plugin. Then, we can test the look up.

In order to make the authentication pluggable, the principal
authenticator plugin relies on 3 interfaces: 

- IAccountStatus : if an adaptation exist to this interface from the
  IPrincipal object, it is used to figure out if the principal can
  login or not. It allows the possibility to disable a user account
  and eventually to compute that disability.

- IPasswordChecker: this adapter is used to check the credentials. If
  it doesnt exist (or if the IPrincipal object doesn't provide this
  interface), the authentication is aborted and None is returned.

- IPrincipalInfo: unlike the previous plugin, the Principal Folder
  authenticator doesn't return directly a PrincipalInfo object but
  uses an adapter to retrieve the appropriate principal info
  object. This is required in order to plug specific behavior to our
  authentication system.


Let's first implement a basic IPrincipalObject. Once stored, we'll be
able to start the look ups and the adapters implementations::

  >>> from dolmen.authentication import IPrincipal
  >>> from zope.interface import implements

  >>> class User(object):
  ...     implements(IPrincipal)
  ...
  ...     def __init__(self, id, title=u"", desc=u""):
  ...         self.id = id
  ...         self.title = title or id
  ...         self.description = desc
  ...         self.groups = []

We can verify our implementation against the interface::

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

  >>> site.auth = PAU
  >>> lsm = site.getSiteManager()
  >>> lsm.registerUtility(PAU, IAuthentication)


Introspection
-------------

Imagine you go to a page that anonymous users don't have access to:

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open("http://localhost/site/@@edit")

As you can see, the plug-in redirects you to the login page:

  >>> print browser.url
  http://localhost/@@login?camefrom=%2F%40%40edit
