# Generated by Django 2.0.3 on 2019-05-11 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0100_auto_20190510_0923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ltv',
            name='customer',
        ),
        migrations.DeleteModel(
            name='Ltv',
        ),
    ]
