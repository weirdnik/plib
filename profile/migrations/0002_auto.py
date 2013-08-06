# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field likes on 'User'
        db.create_table('profile_user_likes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm['profile.user'], null=False)),
            ('status', models.ForeignKey(orm['cockpit.status'], null=False))
        ))
        db.create_unique('profile_user_likes', ['user_id', 'status_id'])


    def backwards(self, orm):
        # Removing M2M table for field likes on 'User'
        db.delete_table('profile_user_likes')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cockpit.status': {
            'Meta': {'object_name': 'Status'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'image_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender_set'", 'to': "orm['profile.User']"}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'recipient_set'", 'null': 'True', 'to': "orm['profile.User']"}),
            'tagged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'cockpit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cockpit.Status']", 'symmetrical': 'False'}),
            'tag': ('django.db.models.fields.TextField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'profile.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'background_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'background_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'icbm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignores': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'ignored_users_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['profile.User']"}),
            'ignores_tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'ignored_tag_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['cockpit.Tag']"}),
            'likes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cockpit.Status']", 'symmetrical': 'False'}),
            'love': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'premium': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'django_user_set'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'watches': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'watched_users_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['profile.User']"}),
            'watches_tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'watched_tag_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['cockpit.Tag']"})
        }
    }

    complete_apps = ['profile']