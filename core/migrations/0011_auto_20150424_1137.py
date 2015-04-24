# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150424_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationuser',
            name='domain',
            field=models.CharField(blank=True, max_length=253, null=True, choices=[(b'jabber.wien', b'jabber.wien'), (b'jabber.zone', b'jabber.zone'), (b'xmpp.zone', b'xmpp.zone'), (b'fsinf.at', b'fsinf.at'), (b'jabber.fsinf.at', b'jabber.fsinf.at'), (b'jabber.at', b'jabber.at')]),
        ),
    ]
