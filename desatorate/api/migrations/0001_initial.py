# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import api.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(unique=True, max_length=50)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('second_last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('avatar', models.ImageField(default=b'default.png', help_text=b'Elija imagen de logo (200x200)', verbose_name=b'Avatar', upload_to=api.models.upload_to_avatar)),
                ('phone', models.TextField(max_length=20, null=True, blank=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('birthday', models.DateField(null=True)),
                ('gender', models.IntegerField(null=True, choices=[(b'Mujer', b'Mujer'), (b'Hombre', b'Hombre')])),
                ('register_date', models.DateField(auto_now=True)),
                ('last_modify_date', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='is_active')),
                ('is_staff', models.BooleanField(default=False, verbose_name='is_staff')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('second_last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=20)),
                ('phone', models.TextField(max_length=20)),
                ('request_date', models.DateTimeField(auto_now=True)),
                ('device_os', models.TextField(max_length=20)),
                ('comment', models.CharField(max_length=500)),
                ('status', models.BooleanField(default=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'request',
            },
        ),
        migrations.CreateModel(
            name='UserDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_token', models.TextField(max_length=250)),
                ('device_os', models.TextField(max_length=20)),
                ('status', models.BooleanField(default=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_device',
            },
        ),
    ]
