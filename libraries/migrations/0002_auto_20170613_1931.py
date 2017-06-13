# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='library',
            options={'verbose_name_plural': 'libraries'},
        ),
        migrations.AddField(
            model_name='library',
            name='is_name_default',
            field=models.BooleanField(default=True),
        ),
    ]
