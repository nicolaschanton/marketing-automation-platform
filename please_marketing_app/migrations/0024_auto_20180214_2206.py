# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-14 22:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0023_intercomevent_minimum_basket_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='intercomevent',
            name='geo_city',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='intercomevent',
            name='geo_country',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='intercomevent',
            name='geo_lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='intercomevent',
            name='geo_long',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='intercomevent',
            name='geo_zip_code',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]