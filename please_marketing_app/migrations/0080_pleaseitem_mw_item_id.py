# Generated by Django 2.0.3 on 2018-10-03 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0079_merchant_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='pleaseitem',
            name='mw_item_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
