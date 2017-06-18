# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-17 18:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_auto_20170617_1649'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Author',
        ),
        migrations.AlterField(
            model_name='book',
            name='google_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.GoogleBook'),
        ),
        migrations.AlterField(
            model_name='book',
            name='page_count',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set([('title', 'author')]),
        ),
    ]