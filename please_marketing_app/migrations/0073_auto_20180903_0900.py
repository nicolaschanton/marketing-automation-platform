# Generated by Django 2.0.3 on 2018-09-03 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0072_referrallead'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='referral_counter',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
