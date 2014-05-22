Management
----------

cleanup
_______

The ``cleanup`` management command cleans outdated confirmation keys as well as
old activities by IP addresses. Make sure you execute this command daily or so
to ensure you don't have to much IP address data stored.

If you use a Linux server and virtualenv, you could add
:file:`/etc/cron.d/accounts.example.com` with these contents::

   25 6    * * *   account    cd /home/account/django-xmpp-account && bin/python manage.py cleanup


.. _ejabberd_registrations:

ejabberd_registrations
______________________

The ``ejabberd_registrations`` management command imports new in-band
registrations from ejabberd. It does so by fetching registration messages sent
to ejabberd via its ``registration_watchers`` setting. You need to configure
access credentials in your localsettings:


.. code-block:: python

   EJABBERD_REGISTRATION_BOT = {
      'jid': 'user@example.com',
      'password': '...',
   }

while your ejabberd configuration says:

.. code-block:: yaml

   registration_watchers:
      - "user@example.com"
