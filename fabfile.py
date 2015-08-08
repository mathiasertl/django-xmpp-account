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
import sys

from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

from six.moves import configparser

from fabric.api import local
from fabric.colors import red
from fabric.context_managers import quiet
from fabric.tasks import Task

from fabric_webbuilders import BuildBootstrapTask
from fabric_webbuilders import BuildJqueryTask
from fabric_webbuilders import MinifyCSSTask
from fabric_webbuilders import MinifyJSTask

node_path = os.path.abspath('node_modules')
if os.path.exists(node_path):
    if node_path not in os.environ['PATH']:
        os.environ['PATH'] = '%s/.bin:%s' % (node_path, os.environ['PATH'])

datestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
build_jquery = BuildJqueryTask(
    excludes='-deprecated,-dimensions',
    dest_dir='core/static/lib/jquery/'
)
build_bootstrap = BuildBootstrapTask(
    config='core/static/bootstrap-config.json',
    dest_dir='core/static/lib/bootstrap/'
)
minify_css = MinifyCSSTask(files=[
    'core/static/lib/bootstrap/css/bootstrap.min.css',
    'core/static/lib/font-awesome/css/font-awesome.min.css',
    'core/static/lib/shariff/shariff.min.css',
    'core/static/css/base.css',
], dest='core/static/account-%s.min.css' % datestamp)
minify_js = MinifyJSTask(files=[
    'core/static/lib/jquery/jquery.min.js',
    'core/static/js/base.js',
], dest='core/static/account-%s.min.js' % datestamp)


config = configparser.ConfigParser({
    'remote': 'origin',
    'branch': 'master',
    'user': 'root',
    'group': '',
    'uwsgi-emperor': '',
    'celery-systemd': '',
    'celery-sysv': '',
})
config.read('fab.conf')


class BuildTask(Task):
    def run(self):
        minify_js.run()
        minify_css.run()


class DeployTask(Task):
    def sudo(self, cmd, chdir=True):
        if chdir is True:
            return local('ssh %s sudo sh -c \'"cd %s && %s"\'' % (self.host, self.path, cmd))
        else:
            return local('ssh %s sudo %s' % (self.host, cmd))

    def sg(self, cmd, chdir=True):
        if not self.group:
            return self.sudo(cmd, chdir=chdir)

        sg_cmd = 'ssh %s sudo sg %s -c' % (self.host, self.group)
        if chdir is True:
            return local('%s \'"cd %s && %s"\'' % (sg_cmd, self.path, cmd))
        else:
            return local('%s "%s"' % (sg_cmd, cmd))

    def exists(self, path):
        """Returns True/False depending on if the given path exists."""
        with quiet():
            return self.sudo('test -e %s' % path, chdir=False).succeeded

    def run(self, section='DEFAULT'):
        # get options that have a default:
        remote = config.get(section, 'remote')
        branch = config.get(section, 'branch')
        self.group = config.get(section, 'group')

        # these options are required for deployment
        try:
            self.path = os.path.abspath(config.get(section, 'path'))
        except configparser.NoOptionError:
            print(red('Error: Configure "%s" in section "%s" in fab.conf' % ('path', section)))
            sys.exit(1)

        try:
            self.host = config.get('DEFAULT', 'host')
        except configparser.NoOptionError:
            print(red('Error: Configure "%s" in section "%s" in fab.conf' % ('host', section)))
            sys.exit(1)

        # virtualenv defaults to one level above self.path:
        try:
            self.virtualenv = config.get('DEFAULT', 'virtualenv')
        except configparser.NoOptionError:
            self.virtualenv = os.path.dirname(self.path)

        if self.virtualenv:
            pip = os.path.join(self.virtualenv, 'bin', 'pip')
            python = os.path.join(self.virtualenv, 'bin', 'python')

            # create virtualenv if it does not yet exist
            if self.exists(self.virtualenv) is False:
                self.sudo('mkdir -p %s' % self.virtualenv, chdir=False)
            if self.exists(python) is False:
                self.sudo('virtualenv %s' % self.virtualenv, chdir=False)
        else:
            pip = 'pip'
            python = 'python'

        # start actually deployment
        local('git push %s %s' % (remote, branch))
        if self.group:
            self.sudo('chgrp -R %s .' % self.group)
        self.sg("git fetch %s" % remote)
        self.sg("git pull %s %s" % (remote, branch))
        self.sg("%s install -U pip" % pip)
        self.sg("%s install -r requirements.txt" % pip)
        self.sg("%s manage.py update" % python)
        if self.group:
            self.sudo('chmod -R o-rwx .')

        uwsgi_emperor = config.get(section, 'uwsgi-emperor')
        if uwsgi_emperor:
            if os.path.isabs(uwsgi_emperor):
                self.sudo("touch %s" % uwsgi_emperor, chdir=False)
            else:
                self.sudo("touch /etc/uwsgi-emperor/vassals/%s.ini" % uwsgi_emperor, chdir=False)

        celery_systemd = config.get(section, 'celery-systemd')
        if celery_systemd:
            self.sudo('service %s restart' % celery_systemd, chdir=False)
        celery_sysv = config.get(section, 'celery-sysv')
        if celery_sysv:
            self.sudo('/etc/init.d/%s restart' % celery_sysv, chdir=False)


deploy = DeployTask()
build = BuildTask()
