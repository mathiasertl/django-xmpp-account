# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150410_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationuser',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='registrationuser',
            name='jid',
            field=models.CharField(default='', unique=True, max_length=509, verbose_name='JID'),
            preserve_default=False,
        ),
    ]
