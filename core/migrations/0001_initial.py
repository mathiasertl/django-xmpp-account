# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RegistrationUser'
        db.create_table(u'core_registrationuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1023)),
            ('domain', self.gf('django.db.models.fields.CharField')(default='jabber.at', max_length=253)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('registered', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('confirmed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['RegistrationUser'])

        # Adding unique constraint on 'RegistrationUser', fields ['username', 'domain']
        db.create_unique(u'core_registrationuser', ['username', 'domain'])

        # Adding model 'Confirmation'
        db.create_table(u'core_confirmation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.RegistrationUser'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('purpose', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'core', ['Confirmation'])

        # Adding model 'Address'
        db.create_table(u'core_address', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39)),
        ))
        db.send_create_signal(u'core', ['Address'])

        # Adding model 'UserAddresses'
        db.create_table(u'core_useraddresses', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Address'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.RegistrationUser'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('purpose', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal(u'core', ['UserAddresses'])


    def backwards(self, orm):
        # Removing unique constraint on 'RegistrationUser', fields ['username', 'domain']
        db.delete_unique(u'core_registrationuser', ['username', 'domain'])

        # Deleting model 'RegistrationUser'
        db.delete_table(u'core_registrationuser')

        # Deleting model 'Confirmation'
        db.delete_table(u'core_confirmation')

        # Deleting model 'Address'
        db.delete_table(u'core_address')

        # Deleting model 'UserAddresses'
        db.delete_table(u'core_useraddresses')


    models = {
        u'core.address': {
            'Meta': {'object_name': 'Address'},
            'activities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.RegistrationUser']", 'through': u"orm['core.UserAddresses']", 'symmetrical': 'False'}),
            'address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'core.confirmation': {
            'Meta': {'object_name': 'Confirmation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'purpose': ('django.db.models.fields.SmallIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.RegistrationUser']"})
        },
        u'core.registrationuser': {
            'Meta': {'unique_together': "((u'username', u'domain'),)", 'object_name': 'RegistrationUser'},
            'confirmed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'default': "'jabber.at'", 'max_length': '253'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'registered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1023'})
        },
        u'core.useraddresses': {
            'Meta': {'object_name': 'UserAddresses'},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Address']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'purpose': ('django.db.models.fields.SmallIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.RegistrationUser']"})
        }
    }

    complete_apps = ['core']