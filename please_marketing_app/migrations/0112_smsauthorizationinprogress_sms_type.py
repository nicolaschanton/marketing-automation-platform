# Generated by Django 2.0.3 on 2019-06-17 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0111_smsauthorizationinprogress'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsauthorizationinprogress',
            name='sms_type',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
