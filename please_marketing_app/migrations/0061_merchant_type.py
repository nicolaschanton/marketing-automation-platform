# Generated by Django 2.0.3 on 2018-06-07 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0060_merchant_mw_offers_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='type',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
