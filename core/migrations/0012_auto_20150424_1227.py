# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20150424_1137'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='registrationuser',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='registrationuser',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='registrationuser',
            name='username',
        ),
    ]
