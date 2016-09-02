# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-02 10:27
from __future__ import unicode_literals

from django.db import migrations

def migrate_purpose(apps, schema_editor):
    UserAddress = apps.get_model('core', 'UserAddresses')

    # we don't use constants here because they will be switched in the future
    UserAddress.objects.filter(purpose=0).update(new_purpose='register')
    UserAddress.objects.filter(purpose=1).update(new_purpose='password')
    UserAddress.objects.filter(purpose=2).update(new_purpose='email')
    UserAddress.objects.filter(purpose=3).update(new_purpose='delete')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_useraddresses_new_purpose'),
    ]

    operations = [
        migrations.RunPython(migrate_purpose),
    ]
