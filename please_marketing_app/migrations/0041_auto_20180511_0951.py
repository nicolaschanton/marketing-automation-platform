# Generated by Django 2.0.3 on 2018-05-11 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0040_auto_20180511_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='w_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='w_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
