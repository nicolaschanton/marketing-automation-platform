# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-23 15:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0032_auto_20180223_1514'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='inside_perimeter',
        ),
    ]