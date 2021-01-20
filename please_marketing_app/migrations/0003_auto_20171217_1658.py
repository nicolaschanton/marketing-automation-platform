# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-17 16:58
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0002_auto_20171216_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='categories_purchased',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='merchants_purchased',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='universes_purchased',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='customer',
            name='vouchers_used',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='intercomevent',
            name='item_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
        ),
    ]