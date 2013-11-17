Backends
--------

The :ref:`setting-XMPP_BACKENDS` setting configures the backend that your site
uses. The backend is used to communicate with your Jabber server(s) and register
accounts and so on. Various backends are availabe, if you want to implement your
own backend please see :ref:`custom-backends` below.

.. autoclass:: backends.ejabberdctl.EjabberdctlBackend

.. autoclass:: backends.ejabberd_xmlrpc.EjabberdXMLRPCBackend

.. autoclass:: backends.dummy.DummyBackend

.. _custom-backends:

Custom backends
_______________

.. automodule:: backends.base
   :members:
