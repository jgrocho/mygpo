# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-07 12:13
from __future__ import unicode_literals

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=64), size=None)),
                ('state', models.CharField(max_length=32)),
                ('created', models.DateTimeField(default=datetime.datetime.utcnow)),
            ],
        ),
    ]