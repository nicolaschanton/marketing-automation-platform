# Generated by Django 2.0.3 on 2019-09-06 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_referral_program', '0002_auto_20180922_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='referrallead',
            name='sent_to_intercom',
            field=models.BooleanField(default=False),
        ),
    ]
