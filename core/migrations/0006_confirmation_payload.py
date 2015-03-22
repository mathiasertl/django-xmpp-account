# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_registrationuser_gpg_fingerprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmation',
            name='payload',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
