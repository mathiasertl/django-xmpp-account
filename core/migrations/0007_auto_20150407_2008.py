# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_confirmation_payload'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=255)),
                ('domain', models.CharField(default=b'jabber.at', max_length=253, choices=[(b'jabber.org', b'jabber.org'), (b'jabber.at', b'jabber.at')])),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('gpg_fingerprint', models.CharField(max_length=40, null=True, blank=True)),
                ('registration_method', models.SmallIntegerField(choices=[(0, 'Via Website'), (1, 'In-Band Registration'), (99, 'Unknown')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('confirmed', models.DateTimeField(null=True, blank=True)),
            ],
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
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('username', 'domain')]),
        ),
    ]
