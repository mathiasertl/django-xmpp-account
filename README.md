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
installation](#Basic installation)) or all dependencies manually installed.

### Requirements

* Currently only [ejabberd](https://www.ejabberd.im) via `mod_xmlrpc` is supported. If you want to
  use a different server, please consider [contributing your own backend](#Custom backends).

### Basic installation

### Configuration

### Database setup

### Webserver setup

## Custom backends

## Regenerate JavaScript/CSS

The site uses minified JavaScript and CSS for faster pageloads. If you change a JS/CSS file, you
must regenerate the minifed files:

```
sudo apt-get install nodejs npm
# Ubunut installs node as nodejs, but we need "node"
sudo sudo ln -s /usr/bin/nodejs /usr/local/bin/node 
npm install clean-css uglify-js
