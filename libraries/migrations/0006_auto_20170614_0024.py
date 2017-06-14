# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-14 00:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libraries', '0005_auto_20170613_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='library',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='home_library', serialize=False, to='accounts.UserProfile'),
        ),
        migrations.AlterField(
            model_name='library',
            name='users',
            field=models.ManyToManyField(null=True, related_name='libraries', to='accounts.UserProfile'),
        ),
    ]