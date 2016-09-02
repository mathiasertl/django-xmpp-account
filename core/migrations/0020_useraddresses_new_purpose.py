# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-02 10:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160902_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddresses',
            name='new_purpose',
            field=models.CharField(choices=[('register', 'registration'), ('password', 'set password'), ('email', 'set email'), ('delete', 'delete')], max_length=12, null=True),
        ),
    ]