try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)


from interfaces import IUser, IUserDirectory
from base_plugin import initialize_auth
from validation import UserRegistrationError
from interfaces import IPassProtected, IChangePassword
from interfaces import IPrincipal, IAccountStatus
from events import UserLoginEvent, UserLogoutEvent
from events import IUserLoggedInEvent, IUserLoggedOutEvent

import browser
