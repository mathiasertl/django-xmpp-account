# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(unique=True, max_length=255)),
                ('domain', models.CharField(default=b'jabber.at', max_length=253, choices=[(b'jabber.org', b'jabber.org'), (b'jabber.at', b'jabber.at')])),
                ('email', models.EmailField(max_length=75, unique=True, null=True)),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('confirmed', models.DateTimeField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'User',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.GenericIPAddressField()),
            ],
            options={
                'verbose_name': 'IP-Address',
                'verbose_name_plural': 'IP-Addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Confirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=40)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('purpose', models.SmallIntegerField(choices=[(0, 'registration'), (1, 'set password'), (2, 'set email'), (3, 'delete')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserAddresses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('purpose', models.SmallIntegerField(choices=[(0, 'registration'), (1, 'set password'), (2, 'set email'), (3, 'delete')])),
                ('address', models.ForeignKey(to='core.Address')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'IP-Address Activity',
                'verbose_name_plural': 'IP-Address Activities',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='address',
            name='activities',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='core.UserAddresses'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='registrationuser',
            unique_together=set([('username', 'domain')]),
        ),
    ]
