# Generated by Django 2.0.3 on 2018-06-05 14:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0059_auto_20180605_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='mw_offers_id',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=2000, null=True), blank=True, null=True, size=None),
        ),
    ]
