# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-16 09:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0026_auto_20180215_1847'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='social_profiles',
            new_name='social_profiles_intercom',
        ),
        migrations.AddField(
            model_name='customer',
            name='sent_to_full_contact_api',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='customer',
            name='sent_to_gender_api',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='customer',
            name='social_profiles_full_contact',
            field=models.CharField(blank=True, max_length=100000, null=True),
        ),
    ]