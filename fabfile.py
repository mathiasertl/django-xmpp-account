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


from fabric_webbuilders import BuildBootstrapTask
from fabric_webbuilders import BuildJqueryTask
from fabric_webbuilders import MinifyCSSTask
from fabric_webbuilders import MinifyJSTask


build_jquery = BuildJqueryTask(
    excludes='-ajax,-deprecated,-dimensions,-effects,-offset',
    dest_dir='core/static/lib/jquery/'
)
build_bootstrap = BuildBootstrapTask(
    dest_dir='core/static/lib/bootstrap/'
)
minify_css = MinifyCSSTask(files=[
    'core/static/lib/bootstrap/css/bootstrap.min.css',
    'core/static/lib/bootstrap/css/bootstrap-theme.min.css',
    'core/static/css/base.css',
], dest='core/static/account.min.css')
minify_js = MinifyJSTask(files=[
    'core/static/lib/jquery/jquery.min.js',
    'core/static/js/base.js',
], dest='core/static/account.min.js')

