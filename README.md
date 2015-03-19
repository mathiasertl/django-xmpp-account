# django-xmpp-account

[![Flattr this git
repo](http://api.flattr.com/button/flattr-badge-large.png)](http://flattr.com/thing/3969667/jabber-at-Jabber-for-everyone)

`django-xmpp-account` is a stand-alone Django application that manages registrations to your
Jabber/XMPP server. It was written for [account.jabber.at](https://account.jabber.at) but can be
used for any Jabber/XMPP server. Users can also use the site to reset their password or their email
address or delete their account.

## Features

1. Users can use the site to register an account, reset their password or email address or delete
   their account.
2. Supports Python 2.7+ and Python 3.4+.
3. Fully localized, translation is available in German.
4. As standard [Django](https://www.djangoproject.com/) application, it runs on any WSGI capable
   webserver and supports e.g. MySQL, PostgreSQL.
5. Currently works only with [ejabberd](https://www.ejabberd.im/) (via `mod_xmlrpc`), but could
   easily extended to work with other servers.
6. Robust anti-SPAM features including ReCAPTCHA support, email confirmations and configurable
   rate-limiting.
7. Manages accounts on multiple XMPP servers, page will adapt to the URL used (e.g. see how the
   default XMPP domain changes on [account.jabber.at](https://account.jabber.at) and
   [account.xmpp.zone](https://account.xmpp.zone).
8. Users can give a GPG key (either via fingerprint or direct upload) so the site can use GPG to
   sign and encrypt any confirmation emails it sends.
9. Facebook and Twitter integration via "Like" and "Tweet" buttons. Buttons require two clicks to
   protect the users privacy (see e.g. "[Two clicks for more
   privacy](http://www.h-online.com/features/Two-clicks-for-more-privacy-1783256.html)"). 


This project currently only interacts with ejabberd servers (either via the
`ejabberdctl` command line tool or via the `ejabberd_xmlrpc` plugin), because
this is what [we](https://jabber.at) run. But it is written in a way that you
just have to implement a certain subclass to make it communicate with other
servers. Please feel free to contribute additional backends to this project via
a merge request!

## Documentation

**Preface:** This documentation assumes you are already running your own Jabber/XMPP server. It
also assumes system administration knowledge. `django-xmpp-account` is a
[Django](https://www.djangoproject.im) project, which typically run inside a virtualenv. This means
that all references to any `python` invocation assume that you have it activated (see [Basic
installation](#basic-installation)) or all dependencies manually installed.

### Requirements

* Currently only [ejabberd](https://www.ejabberd.im) via `mod_xmlrpc` is supported. If you want to
  use a different server, please consider [contributing your own backend](#custom-backends).
* Python 2.7 or Python 3.4 (Note: ReCAPTCHA support currently does not work with Python 3 due to
  library issues).
* We strongly recommend you run the project inside a
  [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and install all Python
  library requirements from there. If you don't want to use virtualenv, all used libraries are
  listed in `requirements.txt`, older versions are not tested but are probably fine for most
  libraries.
* Any database that Django supports, for example MySQL or PostgreSQL.

### Basic installation

Simply clone the project, setup a `virtualenv` and install the requirements:

```
git clone https://github.com/mathiasertl/django-xmpp-account.git
cd django-xmpp-account
virtualenv .
source bin/activate
pip install -r requirements.txt
```

### Configuration

The project is configured via the file `xmppaccount/localsettings.py`. There is an example config
file in `xmppaccount/localsettings.py.example`, simply copy it and fill in the details for your
preferred setup. The file is imported by a standard Django settings file, so you can use any of the
[official settings](https://docs.djangoproject.com/en/dev/ref/settings/), even if they are not
documented in the examples file.

### Database setup

The database the project uses is configured by the `DATABASES` setting in
`xmppaccount/localsettings.py`. Also see the [official
documentation](https://docs.djangoproject.com/en/dev/ref/settings/#databases) for possible options.
Make sure the database exists and the configured user has sufficient permissions, and simply
execute:

```
python manage.py migrate
```
... to create all the databases tables.

### Webserver setup

There are many ways to run a standard WSGI application like this one. The WSGI file is located in
`xmppaccount/wsgi.py`. For example, you might want to use
[mod_wsgi](https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/) or [uWSGI and
nginx](http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html). uWSGI can also
be used [with Apache](http://uwsgi-docs.readthedocs.org/en/latest/Apache.html).

A Django project does not serve static files (like JavaScript or CSS files) by itself, this should
be done by the webserver. Configure your webserver to serve the directory configured with the
`STATIC_ROOT` setting under the location configured with the `STATIC_URL` setting. Then collect all
static files there with:

```
python manage.py collectstatic
```

### Generate translations

`django-xmpp-account` is a fully internationalized project, currently a German translation is
available. Generate the translation files with:

```
python manage.py compilemessages
```

### GPG setup

`django-xmpp-account` sends out confirmation emails on any action. Emails can be encrypted if users
upload their private key, but for emails to also be signed, you must generate a private key. You
can simply do this with:

```
python manage.py genkey <hostname>
```

Where `<hostname>` is any of the hosts you configured in the `XMPP_HOSTS` settings. You must then
manually add the key to the respective `XMPP_HOSTS` setting. The key is also saved to the `static/`
directory, so you must update your staticfiles with `python manage.py collectstatic`.

**WARNING:** GPG is very strict about permissions to its configuration directory. Make sure the
directory is owned and read/writeable only by the system user the webserver runs as. The `genkey`
command must also be executed as that same user, which will also create the GPG config directory if
it doesn't exist.

## Update

When want to update the project, simply do (don't forget to activate the virtualenv!):

```
source bin/activate
git fetch
git pull origin master
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py compilemessages
```

Don't forget to restart your webserver afterwards.

## Custom backends

## Regenerate JavaScript/CSS

The site uses minified JavaScript and CSS for faster pageloads. If you change a JS/CSS file, you
must regenerate the minifed files:

```
sudo apt-get install nodejs npm
# Ubunut installs node as nodejs, but we need "node"
sudo sudo ln -s /usr/bin/nodejs /usr/local/bin/node 
npm install clean-css uglify-js
