# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_confirmation_payload'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationuser',
            name='jid',
            field=models.CharField(max_length=255, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='registrationuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='registrationuser',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
    ]
