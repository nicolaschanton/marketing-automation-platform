# Generated by Django 2.0.3 on 2018-09-23 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_growth_hack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basesiren',
            name='l7_declaree',
            field=models.CharField(blank=True, max_length=38, null=True),
        ),
        migrations.AddField(
            model_name='basesiren',
            name='l7_normalisee',
            field=models.CharField(blank=True, max_length=38, null=True),
        ),
    ]
