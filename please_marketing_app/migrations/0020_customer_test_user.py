# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-13 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0019_auto_20180212_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='test_user',
            field=models.NullBooleanField(),
        ),
    ]