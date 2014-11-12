# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20140910_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationuser',
            name='registration_method',
            field=models.SmallIntegerField(default=99, choices=[(0, 'Via Website'), (1, 'In-Band Registration'), (99, 'Unknown')]),
            preserve_default=False,
        ),
    ]
