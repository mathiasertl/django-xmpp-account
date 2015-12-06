# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def lowercase(apps, schema_editor):
    RegistrationUser = apps.get_model('core', 'RegistrationUser')
    for user in RegistrationUser.objects.all():
        lowercased = user.node.lower()
        if lowercased != user.node:
            user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_registrationuser_registration_method'),
    ]

    operations = [
        migrations.RunPython(lowercase),
    ]
