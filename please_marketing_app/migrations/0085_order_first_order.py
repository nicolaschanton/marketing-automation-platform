# Generated by Django 2.0.3 on 2018-10-24 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0084_order_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='first_order',
            field=models.NullBooleanField(),
        ),
    ]