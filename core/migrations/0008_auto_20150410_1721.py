# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_jid(apps, schema_editor):
    RegistrationUser = apps.get_model('core', 'RegistrationUser')
    for u in RegistrationUser.objects.all():
        u.jid = '%s@%s' % (u.username, u.domain)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150410_1721'),
    ]

    operations = [
        migrations.RunPython(set_jid),
    ]
