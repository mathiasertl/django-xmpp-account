# -*- coding: utf-8 -*-
#
# This file is part of xmppregister (https://account.jabber.at/doc).
#
# xmppregister s free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppregister is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmppregister.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from importlib import import_module

from django.conf import settings

from backends.base import InvalidXmppBackendError


DEFAULT_BACKEND_ALIAS = 'default'


def parse_backend_conf(backend, **kwargs):
    conf = settings.XMPP_BACKENDS.get(backend, None)
    if conf is not None:
        args = conf.copy()
        args.update(kwargs)
        backend = args.pop('BACKEND')
        return backend, args
    else:
        raise InvalidXmppBackendError("Could not find backend '%s'" % backend)


def get_backend(backend, **kwargs):
    try:
        backend, params = parse_backend_conf(backend)
        mod_path, cls_name = backend.rsplit('.', 1)
        mod = import_module(mod_path)
        backend_cls = getattr(mod, cls_name)
    except (AttributeError, ImportError) as e:
        raise InvalidXmppBackendError(
            "Could not find backend '%s': %s" % (backend, e))
    backend = backend_cls(**params)
    return backend


backend = get_backend(DEFAULT_BACKEND_ALIAS)
