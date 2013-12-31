`django-xmpp-account` is a small stand-alone Django application that manages
registrations to your Jabber/XMPP server. It was written for
[account.jabber.at](https://account.jabber.at) but can be used for any
Jabber/XMPP server.  It features many anti-SPAM features to limit abuse of your
server. It also allows users to reset their password, set a new Email address
or even delete their account - the former two are not available via the XMPP
protocol, the latter is not available in all clients.

This project currently only interacts with ejabberd servers (either via the
`ejabberdctl` command line tool or via the `ejabberd_xmlrpc` plugin), because
this is what [we](https://jabber.at) run. But it is written in a way that you
just have to implement a certain subclass to make it communicate with other
servers. Please feel free to contribute additional backends to this project via
a merge request!
