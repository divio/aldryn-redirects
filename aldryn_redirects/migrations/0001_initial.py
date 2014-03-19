# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RedirectTranslation'
        db.create_table(u'aldryn_redirects_redirect_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('new_path', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['aldryn_redirects.Redirect'])),
        ))
        db.send_create_signal(u'aldryn_redirects', ['RedirectTranslation'])

        # Adding unique constraint on 'RedirectTranslation', fields ['language_code', 'master']
        db.create_unique(u'aldryn_redirects_redirect_translation', ['language_code', 'master_id'])

        # Adding model 'Redirect'
        db.create_table(u'aldryn_redirects_redirect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='redirects_hvad_set', to=orm['sites.Site'])),
            ('old_path', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'aldryn_redirects', ['Redirect'])

        # Adding unique constraint on 'Redirect', fields ['site', 'old_path']
        db.create_unique(u'aldryn_redirects_redirect', ['site_id', 'old_path'])

    def backwards(self, orm):
        # Removing unique constraint on 'Redirect', fields ['site', 'old_path']
        db.delete_unique(u'aldryn_redirects_redirect', ['site_id', 'old_path'])

        # Removing unique constraint on 'RedirectTranslation', fields ['language_code', 'master']
        db.delete_unique(u'aldryn_redirects_redirect_translation', ['language_code', 'master_id'])

        # Deleting model 'RedirectTranslation'
        db.delete_table(u'aldryn_redirects_redirect_translation')

        # Deleting model 'Redirect'
        db.delete_table(u'aldryn_redirects_redirect')

    models = {
        u'aldryn_redirects.redirect': {
            'Meta': {'ordering': "('old_path',)", 'unique_together': "(('site', 'old_path'),)", 'object_name': 'Redirect'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'redirects_hvad_set'", 'to': u"orm['sites.Site']"})
        },
        u'aldryn_redirects.redirecttranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'RedirectTranslation', 'db_table': "u'aldryn_redirects_redirect_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['aldryn_redirects.Redirect']"}),
            'new_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['aldryn_redirects']
