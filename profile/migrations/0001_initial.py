# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-12 17:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cockpit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('love', models.BooleanField(default=False)),
                ('premium', models.BooleanField(default=False)),
                ('official', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('about', models.TextField(blank=True, null=True)),
                ('icbm', models.TextField(blank=True, null=True)),
                ('sex', models.CharField(choices=[(b'm', b'm'), (b'f', b'f'), (b'o', b'o'), (b'n', b'nie dotyczy')], default=b'o', max_length=1)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=b'avatars/%s')),
                ('background', models.ImageField(blank=True, height_field=b'background_height', null=True, upload_to=b'backgrounds/%s', width_field=b'background_width')),
                ('background_height', models.IntegerField(blank=True, null=True)),
                ('background_width', models.IntegerField(blank=True, null=True)),
                ('phone', models.TextField(blank=True, null=True)),
                ('private', models.BooleanField(default=False)),
                ('ignores', models.ManyToManyField(blank=True, null=True, related_name='ignored_users_set', to='profile.User')),
                ('ignores_tags', models.ManyToManyField(blank=True, null=True, related_name='ignored_tag_set', to='cockpit.Tag')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='django_user_set', to=settings.AUTH_USER_MODEL)),
                ('watches', models.ManyToManyField(blank=True, null=True, related_name='watched_users_set', to='profile.User')),
                ('watches_tags', models.ManyToManyField(blank=True, null=True, related_name='watched_tag_set', to='cockpit.Tag')),
            ],
        ),
    ]
