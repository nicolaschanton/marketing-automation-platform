# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-12 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0018_auto_20180211_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intercomevent',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
