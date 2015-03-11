# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-account (https://account.jabber.at/doc).
#
# django-xmpp-account is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# django-xmpp-account is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import logging
import os
logging.basicConfig(level=logging.DEBUG)

from fabric.api import env
from fabric.api import local
from fabric.context_managers import cd
from fabric.tasks import Task

from fabric_webbuilders import BuildBootstrapTask
from fabric_webbuilders import BuildJqueryTask
from fabric_webbuilders import MinifyCSSTask
from fabric_webbuilders import MinifyJSTask


build_jquery = BuildJqueryTask(
    excludes='-deprecated,-dimensions,-effects,-offset',
    dest_dir='core/static/lib/jquery/'
)
build_bootstrap = BuildBootstrapTask(
    config='core/static/bootstrap-config.json',
    dest_dir='core/static/lib/bootstrap/'
)
minify_css = MinifyCSSTask(files=[
    'core/static/lib/bootstrap/css/bootstrap.min.css',
    'core/static/css/base.css',
], dest='core/static/account.min.css')
minify_js = MinifyJSTask(files=[
    'core/static/lib/jquery/jquery.min.js',
    'core/static/js/base.js',
], dest='core/static/account.min.js')

class DeployTask(Task):
    def run(self, host='hyperion', dir='/usr/local/home/xmpp-account/django-xmpp-account/', group='xmpp-account'):
        local('git push')
        ssh = lambda cmd: local('ssh %s sudo sg %s -c \'"cd %s && %s"\'' % (host, group, dir, cmd))
        ssh("git fetch")
        ssh("git pull origin master")
        ssh("../bin/pip install -r requirements.txt")
        ssh("../bin/python manage.py update")
        ssh("touch /etc/uwsgi-emperor/vassals/xmpp-account.ini")


deploy = DeployTask()
