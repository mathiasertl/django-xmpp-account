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

Implementing your own backend is easy. Simply:

#. Subclass :py:class:`.XmppBackendBase` and implement all functions.

   #. The constructor should take all settings you want to use in
      :ref:`settings-XMPP_BACKENDS` as (upper case!) keyword arguments.
   #. Make sure that all functions use the same parameter names as in the base
      class. All function arguments are passed as keyword arguments.
   #. If a setting is optional, provide a sensible default value.
   #. Raise :py:exc:`.UserExists` if the user already exists and
      :py:exc:`.UserNotFound` if the user is not found.

#. Configure :ref:`settings-XMPP_BACKENDS` to use your new backend.


.. autoclass:: backends.base.XmppBackendBase
   :members:

.. autoexception:: backends.base.BackendError

.. autoexception:: backends.base.InvalidXmppBackendError

.. autoexception:: backends.base.UserExists

.. autoexception:: backends.base.UserNotFound
