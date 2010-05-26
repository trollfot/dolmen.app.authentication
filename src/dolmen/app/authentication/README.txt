*************************
dolmen.app.authentication
*************************

``dolmen.app.authentication`` is the package responsible for the users
groups managements in a Dolmen application. Built on the on the top of
``dolmen.authentication``, it provides a set of plugins and base
classes that can help building a complex users & groups system.

Credentials plugins
===================

Credentials plugins are responsible for the extraction of credentials,
in order to identify a user. ``dolmen.app.authentication`` provides a
single plugin, out of the box.

Cookies Credentials
-------------------

The cookie credentials plugin extracts the credentials from cookies.

FIXME



Authenticator Plugins
=====================

Authenticator plugins uses extracted credentials in order to retrieve
and identify principals. ``dolmen.app.authentication`` provides two
plugins.


Global Registry Authentication
------------------------------

In order to register principals, the ``zope.principalregistry``
package provides a global registry that is not persistent and
re-constructed at each startup. The Global Registry Authenticator is
meant to look up the principal inside that global registry.

  >>> from zope.pluggableauth.interfaces import IAuthenticatorPlugin
  >>> from dolmen.app.authentication import plugins
  >>> IAuthenticatorPlugin.implementedBy(plugins.GlobalRegistryAuth)
  True

We verify the integrity of our implementation against the
requirements::

  >>> from zope.interface.verify import verifyObject
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
authenticator plugin relies on 3 adapters: 

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

  >>> stilgar = User(u"stilgar")
  >>> verifyObject(IPrincipal, stilgar)
  True

  >>> plugin['stilgar'] = stilgar
  >>> print [user for user in plugin.keys()]
  [u'stilgar']

  >>> found = plugin.authenticateCredentials(
  ...            {'login': 'stilgar', 'password': 'boo'})

  >>> found is None
  True
