# django-xmpp-account

[![Flattr this git
repo](http://api.flattr.com/button/flattr-badge-large.png)](http://flattr.com/thing/3969667/jabber-at-Jabber-for-everyone)

`django-xmpp-account` is a stand-alone Django application that manages registrations to your
Jabber/XMPP server. It was written for [account.jabber.at](https://account.jabber.at) but can be
used for any Jabber/XMPP server. Users can also use the site to reset their password or their email
address or delete their account.

## Features

1.  Users can use the site to register an account, reset their password or email address or delete
    their account.
2.  Supports Python 2.7+ and Python 3.4+.
3.  Fully localized, translation is available in German.
4.  As standard [Django](https://www.djangoproject.com/) application, it runs on any WSGI capable
    webserver and supports e.g. MySQL, PostgreSQL.
5.  Currently works only with [ejabberd](https://www.ejabberd.im/) (via `mod_xmlrpc`), but could
    easily extended to work with other servers.
6.  Robust anti-SPAM features including ReCAPTCHA support, email confirmations and configurable
    rate-limiting.
7.  Manages accounts on multiple XMPP servers, page will adapt to the URL used (e.g. see how the
    default XMPP domain changes on [account.jabber.at](https://account.jabber.at) and
    [account.xmpp.zone](https://account.xmpp.zone).
8.  Users can give a GPG key (either via fingerprint or direct upload) so the site can use GPG to
    sign and encrypt any confirmation emails it sends.
9.  Support for [Celery](http://docs.celeryproject.org) to send emails asynchronously for fast page
    response times.
10. Facebook and Twitter integration via "Share" and "Tweet" buttons. Buttons use
    [Shariff](https://github.com/heiseonline/shariff) to protect users privacy.
11. Fabric file for fast and automated deployment of updates.

This project currently only interacts with ejabberd servers (either via the
`ejabberdctl` command line tool or via the `ejabberd_xmlrpc` plugin), because
this is what [we](https://jabber.at) run. But it is written in a way that you
just have to implement a certain subclass to make it communicate with other
servers. Please feel free to contribute additional backends to this project via
a merge request!

## Documentation

**Preface:** This documentation assumes you are already running your own Jabber/XMPP server. It
also assumes system administration knowledge. `django-xmpp-account` is a
[Django](https://www.djangoproject.im) project which typically runs inside a virtualenv. This means
that all references to any `python` invocation assume that you have it activated (see [Basic
installation](#basic-installation)) or all dependencies manually installed.

### Requirements

* Currently only [ejabberd](https://www.ejabberd.im) via `mod_xmlrpc` is supported. If you want to
  use a different server, please consider [contributing your own backend](#custom-backends).
* Python 2.7 or Python 3.4 (Note: ReCAPTCHA support currently does not work with Python 3 due to
  library issues).
* We strongly recommend you run the project inside a
  [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and install all Python
  library requirements inside. If you don't want to use virtualenv, all used libraries are listed
  in `requirements.txt`, older versions are not tested but are probably fine for most libraries.
* Any database that Django supports, for example MySQL or PostgreSQL.
* GnuPG to sign and encrypt confirmation mails.

If you use Debian/Ubuntu, you can copy & paste this command:

```
apt-get install gcc python-virtualenv gnupg libxml2-dev libxslt1-dev python-dev \
    libfreetype6-dev gettext
```

### Basic installation

Simply clone the project, setup a `virtualenv` and install the requirements:

```
git clone https://github.com/mathiasertl/django-xmpp-account.git
cd django-xmpp-account
virtualenv .
source bin/activate
pip install -r requirements.txt
```

Depending on the database backend you want to use, you probably need to install additional
packages. For MySQL, this would be:

```
apt-get install libmysqlclient-dev mysql-common
pip install MySQL-python
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

**NOTE:** Unless you deactivate GPG support, we highly recommend you enable threading support.

A Django project does not serve static files (like JavaScript or CSS files) by itself, this should
be done by the webserver. Configure your webserver to serve the directory configured with the
`STATIC_ROOT` setting under the location configured with the `STATIC_URL` setting. Then collect all
static files there with:

```
python manage.py collectstatic
```

You can optimize page load speed by using browser caching. See Google's [PageSpeed
Insights](https://developers.google.com/speed/pagespeed/insights/) for more information. Here is
what we use using [mod_expires](http://httpd.apache.org/docs/2.4/de/mod/mod_expires.html):

```
ExpiresActive on
ExpiresDefault "access plus 1 month"
ExpiresByType text/html "access plus 0 seconds"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"

<Location /captcha>
    ExpiresByType image/png "access plus 0 seconds"
</Location>
```

### Generate translations

`django-xmpp-account` is a fully internationalized project, currently a German translation is
available. The project has per-app translations, so to generate the translations manually, you must
execute `manage.py` inside the app directories (`core`, `register`, `reset` and `delete`):

```
cd core
python ../manage.py compilemessages
```

Note that all translations are automatically compiled with `manage.py update`.

### Schedule cron-jobs

The `manage.py cleanup` command removes users from the database if users were removed from the XMPP
server. It also removes users from the database if they registered but never clicked the
confirmation link sent to them via email. 

```
HOME=/usr/local/home/xmpp-account
PATH=/usr/local/home/xmpp-account/bin

# m h   dom mon dow     user            command
22 *    * * *           xmpp-account   python django-xmpp-account/manage.py cleanup
```

If your server allows In-Band Registration (IBR), you can also add the `manage.py
ejabberd_registrations` command. It is an XMPP bot that parses messages that ejabberd sends to
contacts named in its `registration_watchers` setting. Note that it uses additional settings,
please see your `localsettings.py`. 

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

### Celery setup

[Celery](http://docs.celeryproject.org) is a distributed task queue. *django-xmpp-account* can use
celery to send emails asynchronously. This is especially recommended if you enable GPG, since GPG
operations can be quite slow and doing all GPG operations inside the WSGI process will result in
long page load times. The downside is that if some GPG operations fail, no error message can be
displayed anymore and the user will receive an unencrypted email instead.

To enable Celery, just edit the relevant sections in your `localsettings.py` file. We strongly
recommend using `redis` as a broker, on Debian/Ubuntu a simple `apt-get install redis-server`
should suffice.

Celery obviously runs as a daemon, so it needs to be started. Example files for systemd are
included in `files/systemd`. They assume that celery runs as user `xmpp-account` with the home
directory `/usr/local/home/xmpp-account`, a virtualenv and the source code in that directory. If
this doesn't suit your needs, you need to modify the files accordingly. After that, three simple
symlinks should enable the service:

```
ln -s /usr/local/home/xmpp-account/django-xmpp-account/files/systemd/celery-xmpp-account.tmpfiles \
    /etc/tmpfiles.d/celery-xmpp-account.conf
ln -s /usr/local/home/xmpp-account/django-xmpp-account/files/systemd/celery-xmpp-account.conf \
    /etc/conf.d/
ln -s /usr/local/home/xmpp-account/django-xmpp-account/files/systemd/celery-xmpp-account.service \
    /etc/systemd/system/
```

Then just start the celery daemon with:

```
service celery-xmpp-account start
```

If you're not using systemd, the official documentation has a [few more
examples](http://docs.celeryproject.org/en/latest/tutorials/index.html) for other init systems.

## Update

When want to update the project, simply do (don't forget to activate the virtualenv!):

```
source bin/activate
git fetch
git pull origin master
pip install -r requirements.txt
python manage.py update
```

Don't forget to restart your webserver afterwards.

## Deployment

We use a fabric script for easy, fast and reproduceable deployment. If you have local modifications
to this software, you might want to use the script instead.  It's somewhat customizable via the
file `fab.conf`, see the example file in the repositories root directory.

The deployment script pushes a local repository (where you'd write and test your changes) to a
remote, then updates the repository on the deployed host from that. It will also do all other
update-related tasks for you. 

If the fab-file suits your needs (if not: do a merge request!), you should be able to update a
deployment simply by doing:

```
fab deploy
```

## Custom backends

Currently only `ejabberd` via `mod_xmlrpc` is supported. But `django-xmpp-account` was written with
additional backends in mind, so you can easily add support for any custom XMPP server, if you know
a little Python. If you do, please consider doing a pull request for your backend.

To implement support for your own server, simply create a python class that subclasses
`backends.base.XmppBackendBase`. Raise `backends.base.UserExists` if the user already exists and
`backends.base.UserNotFound` if the user is not found. The docstrings document precisely what
Exceptions are expected. Make sure that your backend implements all methods defined by the base
class and the methods use the same argument names (backend functions are always called with
keyword arguments).

## Regenerate JavaScript/CSS

The site uses minified JavaScript and CSS for faster pageloads. If you change a JS/CSS file, you
must regenerate the minifed files:

```
sudo apt-get install nodejs npm
# Ubunut installs node as nodejs, but we need "node"
sudo ln -s /usr/bin/nodejs /usr/local/bin/node 
npm install clean-css uglify-js
```
