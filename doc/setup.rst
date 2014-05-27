Setup
_____

**django-xmpp-account** is a standard `Django`_ project. At a minimum, it
requires:

* `Python`_ 2.6 or later (tested only with Python 2.7)
* `Django`_ 1.6 or later
* `South`_  0.8.2 or later
* `django-brake`_

The project is carefully written to support any XMPP server but at present,
only ejabberd_ integration is implemented. If you care to implement support for
Prosody_ please don't hesitate to do a merge request on github.

When you use ejabberd_, you also need mod_admin_extra installed.

.. _Python: http://www.python.org
.. _Django: https://www.djangoproject.com
.. _South: http://south.aeracode.org/
.. _django-brake: https://github.com/gmcquillan/django-brake

Add user
--------

As a WSGI application, **django-xmpp-account** runs as its own system user. The
source code does not have to belong to that user, it only has to be readable.
On Linux/Unix systems, add a user with::

   adduser --system --group --home=/home/account/ --disabled-login account

Download
--------

The code of **django-xmpp-account** is managed in a `git repository
<https://github.com/mathiasertl/django-xmpp-account>`_. To download
the source, simply do::

   cd /home/account/ && git clone https://github.com/mathiasertl/django-xmpp-account.git

Setup virtualenv
----------------

It is recommended to use a ``virtualenv`` to install the dependencies. This way,
your system is not cluttered with libraries you only need for this project. This
will install all dependencies you need::

   cd django-xmpp-account
   virtualenv .
   source bin/activate
   pip install -r requirements.txt

.. NOTE:: virtualenv is not installed by default on many systems. In
   Debian/Ubuntu, the package is called ``python-virtualenv``.

Configuration
-------------

Simply create a file called :file:`xmppaccount/localsettings.py` with all
configuration directives. All `Django settings`_ are of course supported, as
well as quite a few additional configuration directives (see :doc:`settings` for
a reference on configuration directives for this project).

You can copy :file:`xmppaccount/localsettings.py.example` and fill in the
details to get started super-fast.

.. _Django settings: https://docs.djangoproject.com/en/dev/ref/settings/

Create database
---------------

After you have configured the `DATABASES`_ setting, you have to create the
database and grant the user permissions to it.

MySQL
^^^^^

At a MYSQL prompt, simply execute the following statements (fill in the details
from the `DATABASES`_ setting as appropriate)::

   CREATE DATABASE name CHARACTER SET utf8;
   GRANT ALL PRIVILEGES ON name.* TO 'username'@'host' IDENTIFIED BY 'password';

PostgreSQL
^^^^^^^^^^

Since the author has no PostgreSQL setup, no instructions are provided. If you
can give some, please :doc:`contribute`.

Initialize project
------------------

There is a simple manage.py task that initializes the database, collects static
files and updates translations. If you have correctly configured
`STATIC_ROOT`_ and `DATABASES`_, this should work just fine::

   source bin/activate
   python manage.py update


.. _DATABASES: https://docs.djangoproject.com/en/dev/ref/settings/#databases
.. _DATABASES: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATIC_ROOT

Webserver
---------

Any Webpage obviously needs a webserver. **django-xmpp-account** is a standard
WSGI application, so any webserver capable of hosting WSGI applications will do.
The WSGI script is located at :file:`xmppacount/wsgi.py`.

Here are a few setup instructions for popular webservers:

* `Apache and mod_wsgi
  <https://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide#Mounting_At_Root_Of_Site>`_
* `NGINX and FastCGI <http://wiki.nginx.org/DjangoFastCGI>`_
* `uWSGI <https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/>`_
  (a pure WSGI server, you still need a module for your main webserver)

Here is what we do using Apache and mod_wsgi:

.. code-block:: apache

   # Base python virtualenv (global directive!)
   # see: https://code.google.com/p/modwsgi/wiki/VirtualEnvironments
   WSGIPythonHome /usr/local/share/virtualenv

   <VirtualHost *:443>
      # ... basic configuration skipped

      WSGIScriptAlias / /home/account/django-xmpp-account/xmppaccount/wsgi.py

      # NOTE: wee add the virtualenv path and the project itself to the
      # pythonpath, this way we don't have to modify the wsgi file.
      # "account" is the normal system user/group added above.
      WSGIDaemonProcess account user=account group=account threads=1 python-path=/home/account/django-xmpp-account/:/home/account/django-xmpp-account/lib/python2.7/site-packages
      WSGIProcessGroup account

      # Fix static files. This means that you have the following in
      # localsettings.py:
      #
      # STATIC_ROOT = '/var/www/account.example.com/static/'
      # STATIC_URL = '/static/'
      Alias /static/ /var/www/account.example.com/static/
      <Directory /var/www/account.example.com/static>
          Order deny,allow
          Allow from all
      </Directory>
   </VirtualHost>
