# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-24 15:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0009_auto_20170624_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcopy',
            name='comment',
            field=models.TextField(blank=True, max_length=200),
        ),
    ]
