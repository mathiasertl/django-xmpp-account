# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150410_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationuser',
            name='domain',
            field=models.CharField(default=b'jabber.at', max_length=253, null=True, blank=True, choices=[(b'jabber.wien', b'jabber.wien'), (b'jabber.zone', b'jabber.zone'), (b'xmpp.zone', b'xmpp.zone'), (b'fsinf.at', b'fsinf.at'), (b'jabber.fsinf.at', b'jabber.fsinf.at'), (b'jabber.at', b'jabber.at')]),
        ),
        migrations.AlterField(
            model_name='registrationuser',
            name='username',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
