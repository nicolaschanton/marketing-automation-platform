# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-19 10:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0007_auto_20171219_1002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='category',
        ),
    ]
