# Generated by Django 2.0.3 on 2018-05-25 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0056_auto_20180524_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='first_import_events_done',
            field=models.NullBooleanField(),
        ),
    ]
