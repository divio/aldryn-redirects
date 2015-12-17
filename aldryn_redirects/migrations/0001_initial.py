# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_path', models.CharField(help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.", max_length=200, verbose_name='redirect from', db_index=True)),
                ('site', models.ForeignKey(related_name='redirects_hvad_set', to='sites.Site')),
            ],
            options={
                'ordering': ('old_path',),
                'verbose_name': 'redirect',
                'verbose_name_plural': 'redirects',
            },
        ),
        migrations.CreateModel(
            name='RedirectTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('new_path', models.CharField(help_text="This can be either an absolute path (as above) or a full URL starting with 'http://'.", max_length=200, verbose_name='redirect to', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='aldryn_redirects.Redirect', null=True)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'aldryn_redirects_redirect_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.AlterUniqueTogether(
            name='redirecttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='redirect',
            unique_together=set([('site', 'old_path')]),
        ),
    ]
