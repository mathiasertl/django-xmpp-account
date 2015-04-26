# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def lowercase(apps, schema_editor):
    RegistrationUser = apps.get_model('core', 'RegistrationUser')
    for user in RegistrationUser.objects.all().only('jid'):
        lowercased = user.jid.lower()
        if lowercased != user.jid:
            user.jid = lowercased
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150424_1227'),
    ]

    operations = [
        migrations.RunPython(lowercase),
    ]
