# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-24 17:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0011_auto_20170624_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='library',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libraries.Library'),
        ),
    ]
