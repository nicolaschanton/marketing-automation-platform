# Generated by Django 2.0.3 on 2019-05-10 09:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0099_auto_20190510_0917'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ltv',
            old_name='month',
            new_name='days',
        ),
    ]
