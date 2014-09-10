Settings
--------

As a Django project, this project is configured via a file called :file:`settings.py`. You should
not edit this file yourself (it's in the git repository to provide defaults), but edit the
:file:`xmppaccount/localsettings.py` instead.  If you haven't already, copy the file
:file:`localsettings.py.example` in the same directory and start from there.

This page documents custom settings used by this project, for all other available settings, please
see `Django settings`_.

.. _Django settings: https://docs.djangoproject.com/en/dev/ref/settings/

.. _settings-BLOCKED_EMAIL_TLDS:

BLOCKED_EMAIL_TLDS
__________________

Default: ``set()`` (Empty set)

A set of domains that are not allowed to be used in Email addresses during registration or as a new
Email address for an existing user.

Domains from the :ref:`settings-XMPP_HOSTS` setting that don't have their ``EMAIL`` key set to
``True`` will be automatically be included in this list.

.. _settings-BRAND:

BRAND
_____

Default: ``''`` (Empty string)

The default "brand" displayed on the left of the navigation bar. If not set, the hostname of the
jabber-server (according to :ref:`settings-XMPP_HOSTS_MAPPING` is used instead.

CONTACT_URL
___________

Default:: ``''`` (Empty string)

The default URL where the user may contact the server administrators. This URL is only used when
:ref:`settings-XMPP_HOSTS` does not define a contact URL.

.. _settings-CLEARTEXT_PASSWORDS:

CLEARTEXT_PASSWORDS
___________________

Default:: ``True``

Unless this setting is set to ``False``, the site will display a warning that passwords are stored
in clear text whenever the user is prompted to enter a new password.

.. _settings-CONFIRMATION_TIMEOUT:

CONFIRMATION_TIMEOUT
____________________

Default:: ``timedelta(hours=24)`` (24 hours)

Every action requires an Email confirmation: The user receives an Email, and only if he clicks the
link provided there, he can actually do anything. This setting configures the time the links in the
comfirmation Emails stay valid.

.. _settings-DEFAULT_XMPP_HOST:

DEFAULT_XMPP_HOST
_________________

Default:: see text

The host that is preselected in the dropdown of the registration form. This setting of course has
an effect if you have more then one server. If you do not specify it yourself, an arbitrary host
will be selected on application startup.

.. _settings-EJABBERD_REGISTRATION_BOT:

EJABBERD_REGISTRATION_BOT
_________________________

Bot configuration for import of new registrations from ejabberd. See the
:ref:`ejabberd_registrations` management command for more information.

.. _settings-FORM_TIMEOUT:

FORM_TIMEOUT
____________

Default:: ``3600`` (1 hour)

Maximum amount of time a form stays valid. If the user loads a page and submits it after this many
seconds, he will have to reload the page to get a new form.

.. _settings-MIN_USERNAME_LENGTH:

MIN_USERNAME_LENGTH
___________________

Default:: ``3``

Minimum characters required for the registration of a new username.

.. _settings-MAX_USERNAME_LENGTH:

MAX_USERNAME_LENGTH
___________________

Default:: ``32``

Maximum characters allowed for the registration of a new username. If you provide a value greater
then 255 characters, it will be capped to that value.

.. _settings-RECAPTCHA_PRIVATE_KEY:

RECAPTCHA_PRIVATE_KEY
_____________________

Default:: ``""`` (empty string)

If you set both this setting and :ref:`settings-RECAPTCHA_PUBLIC_KEY`, every form will be protected
by a CAPTCHA.

.. _settings-RECAPTCHA_PUBLIC_KEY:

RECAPTCHA_PUBLIC_KEY
____________________

Default:: ``""`` (empty string)

If you set both this setting and :ref:`settings-RECAPTCHA_PRIVATE_KEY`, every form will be
protected by a CAPTCHA.

.. _settings-REGISTRATION_RATE:

REGISTRATION_RATE
_________________

Default::

   {
       timedelta(minutes=2): 1,
       timedelta(hours=1): 2,
       timedelta(days=1): 5,
   }

This configures how many accounts a single IP address can register within the given timeframes.
Every restriction is added up, if any rate is exceeded, no registration is possible at the given
time. The default means that an IP address can register at most:

* once every two minutes
* twice every hour
* five times per day

If you want to override this setting, make sure you have the ``datetime.timedelta`` imported at the
top of :file:`xmpplist/localsettings.py`::

   from datetime import timedelta

.. _settings-SPAM_BLOCK_TIME:

SPAM_BLOCK_TIME
_______________

Default:: ``86400`` (24 hours)

If the client shows behaviour that clearly identifies it as spambot, it will be blocked for this
amount of seconds.

Clients are identified as spambots if:

* some hidden form fields are given incorrectly
* a form is submitted within one second

.. _settings-WELCOME_MESSAGE:

WELCOME_MESSAGE
_______________

Default:: ``None`` (No message will be sent).

If set to a dictionary, newly registered users will receive a welcome message via XMPP upon
registration. Example::

   WELCOME_MESSAGE = {
      'subject': "Welcome to {domain}!',
      'message': """Dear {username}@{domain},

   We hope you like our server. If you ever loose your password, go to
   {password_reset_url} and an email will be sent to {email}.

   yours, the {domain} team""",
   }

Standard formatting can be applied, as shown above. Availiabe keys are:

================== =====================================================
key
================== =====================================================
username           The username (excluding the domain).
domain             The domain the user registered at.
email              The email address he registered with.
contact_url        URL defined by the ``CONTACT_URL`` setting.
password_reset_url Full URL where the user can reset his/her password.
email_reset_url    Full URL where the user reset the email address.
delete_url         Full URL where the user can delete the account.
================== =====================================================

.. _settings-XMPP_BACKENDS:

XMPP_BACKENDS
_____________

Default:: ``{}`` (Empty dictionary, **required**)

Configure XMPP backends for this site. See :doc:`backends <backends>` for a list of available
backends and their settings. The only required setting is ``BACKEND``, which gives the Python path
to the implementation. Example::

   XMPP_BACKENDS = {
      'default': {
         'BACKEND': 'backends.ejabberd_xmlrpc.EjabberdXMLRPCBackend',
         'USER': 'account.example.com',
         'SERVER': 'account.example.com',
         'PASSWORD': 'super-secure-password',
      }
   }

Currently the only used key for this setting is ``default``.

.. _settings-XMPP_HOSTS:

XMPP_HOSTS
__________

Default: ``{}`` (Empty dictionary, **required**)

A dictionary of the hosts this installation is able to manage. This means that your backend (see
:ref:`settings-XMPP_BACKENDS`) can handle each of these domains.

.. WARNING:: Never remove hosts from this setting entirely unless you have (manually!) removed all
   users from this domain from the database.

   If you want this site to stop managing a given host, set its ``MANAGE`` setting to ``False``.

The value must be a dictionary, with the keys being domains and the values being dictionaries, with
the following possible keys:

.. rubric:: REGISTRATION

Default:: ``False``

A boolean ``True`` means that users should be able to register at this host.

.. rubric:: RESERVATION

Default:: ``False``

A boolean ``True`` means that the backend will reserve the username when the user first registers
(when the confirmation Email is sent to the user). For most backends this means that the user is
created with a randomly generated password and the real password is only set when the user provides
a password at the Email confirmation page.

.. rubric:: MANAGE

Default:: ``True``

Set this value to ``False`` if you want to completely disable a domain but still have local users
in the database.

.. rubric:: EMAIL

Default:: ``False``

Unfortunately people frequently try to give their full Jabber ID as their Email address. Unless you
set this setting to ``True``, users will not be able to fill in Email addresses with this domain in
any form.

.. rubric:: BRAND

Default:: :ref:`settings-BRAND` or :ref:`settings-DEFAULT_XMPP_HOST`

If set, display this brand instead. If you do not want to use a brand, set this to an empty string.

.. rubric:: CONTACT_URL

Default:: :ref:`settings-CONTACT_URL`

An URL where the user may contact the server administrators. This URL is displayed e.g. if the
registration fails, so the URL should provide at least some way to contact you **without** XMPP.


Example::

   XMPP_HOSTS = {
      'jabber.at': {
         'REGISTRATION': True,
         'RESERVATION': True,  # users can also do in-band registration
      },
      'jabber.net': {
         'REGISTRATION': True,
         'RESERVATION': False,  # users can only register through this site
      }
      'oldhost.jabber.at': {
         'MANAGE': False,  # we used this many years back
      }
   }

.. _settings-XMPP_HOSTS_MAPPING:

XMPP_HOSTS_MAPPING
__________________

Default: ``{}``

A mapping of XMPP hosts to HTTP hosts this page is available under. This will change the behaviour
of your site depending on the hostname used. For example, if you use
``https://register.example.com`` to register accounts for ``example.com`` and
``https://account.example.org`` to register accounts for ``example.org``, use::

   XMPP_HOSTS_MAPPING = {
      'register.example.com': 'example.com',
      'account.example.org': 'example.org',
   }

The values of the dictionary must match a host defined in :ref:`settings-XMPP_HOSTS`. If the site
is viewed via an unknown domain (e.g. ``something-else.example.net`` in the above example, the
:ref:`settings-DEFAULT_XMPP_HOST` will be used.
