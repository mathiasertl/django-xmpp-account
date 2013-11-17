Settings
--------

.. _settings-BLOCKED_EMAIL_TLDS:

BLOCKED_EMAIL_TLDS
__________________

Default: ``set()`` (Empty set)

A set of domains that are not allowed to be used in Email addresses during
registration or as a new Email address for an existing user.

Domains from the :ref:`settings-XMPP_HOSTS` setting that don't have their
``EMAIL`` key set to ``True`` will be automatically be included in this list.

.. _settings-CLEARTEXT_PASSWORDS:

CLEARTEXT_PASSWORDS
___________________

Default:: ``True``

TODO

.. _settings-CONFIRMATION_TIMEOUT:

CONFIRMATION_TIMEOUT
____________________

Default:: ``timedelta(hours=24)`` (24 hours)

TODO

.. _settings-FORM_TIMEOUT:

FORM_TIMEOUT
____________

Default:: ``3600`` (1 hour)

TODO

.. _settings-MIN_USERNAME_LENGTH:

MIN_USERNAME_LENGTH
___________________

Default:: ``3``

TODO

.. _settings-MAX_USERNAME_LENGTH:

MAX_USERNAME_LENGTH
___________________

Default:: ``32``

Todo. NOTE: Max 255 characters.

.. _settings-RECAPTCHA_PRIVATE_KEY:

RECAPTCHA_PRIVATE_KEY
_____________________

Default:: ``""`` (empty string)

.. _settings-RECAPTCHA_PUBLIC_KEY:

RECAPTCHA_PUBLIC_KEY
____________________

Default:: ``""`` (empty string)

TODO

.. _settings-REGISTRATION_RATE:

REGISTRATION_RATE
_________________

Default::

   {
       timedelta(seconds=30): 1,
       timedelta(minutes=1): 2,
   }

TODO

.. _settings-SPAM_BLOCK_TIME:

SPAM_BLOCK_TIME
_______________

Default:: ``86400`` (24 hours)

TODO

.. _settings-XMPP_BACKENDS:

XMPP_BACKENDS
_____________

TODO

.. _settings-XMPP_HOSTS:

XMPP_HOSTS
__________

Default: ``{}`` (Empty dictionary)

A dictionary of the hosts this installation is able to manage. This means that
your backend (see :ref:`settings-XMPP_BACKENDS`) can handle each of these
domains.

The value must be a dictionary, with the keys being domains and the values being
dictionaries, with the following possible keys:

* ``REGISTRATION``: A boolean ``True`` means that users should be able to
  register at this host. The default is ``False``.
* ``RESERVATION``: A boolean ``True`` means that the backend will reserve the
  username when the user first registers (when the confirmation Email is sent to
  the user). For most backends this means that the user is created with a
  randomly generated password and the real password is only set when the user
  provides a password at the Email confirmation page. The default is ``False``.
* ``MANAGE``: Set this value to ``False`` if you want to completely disable a
  domain but still have local users in the database.
* ``EMAIL``: Unfortunately people frequently try to give their full Jabber ID as
  their Email address. Unless you set this setting to ``True``, users will not
  be able to fill in Email addresses with this domain in any form.

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
