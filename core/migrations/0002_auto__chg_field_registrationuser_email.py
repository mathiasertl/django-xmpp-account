# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'RegistrationUser.email'
        db.alter_column(u'core_registrationuser', 'email', self.gf('django.db.models.fields.EmailField')(max_length=75, unique=True, null=True))

    def backwards(self, orm):

        # Changing field 'RegistrationUser.email'
        db.alter_column(u'core_registrationuser', 'email', self.gf('django.db.models.fields.EmailField')(default='', max_length=75, unique=True))

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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'unique': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'registered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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