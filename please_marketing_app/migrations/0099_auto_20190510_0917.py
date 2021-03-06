# Generated by Django 2.0.3 on 2019-05-10 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0098_ltv'),
    ]

    operations = [
        migrations.AddField(
            model_name='ltv',
            name='order_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ltv',
            name='total_basket_amount',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ltv',
            name='total_partner_amount',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ltv',
            name='total_please_amount',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ltv',
            name='total_voucher_amount',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
