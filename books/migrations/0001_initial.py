# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-17 15:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=100)),
                ('description', models.TextField(max_length=500)),
                ('page_count', models.IntegerField()),
                ('cover', models.ImageField(upload_to='')),
                ('authors', models.ManyToManyField(to='books.Author')),
            ],
        ),
        migrations.CreateModel(
            name='GoogleBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('google_id', models.CharField(max_length=12)),
                ('ISBN', models.CharField(max_length=13)),
                ('ebook_link', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='google_info',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='books.GoogleBook'),
        ),
    ]