# Generated by Django 2.0.3 on 2018-08-17 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0067_remove_vouchercode_sent_to_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='intercomevent',
            name='voucher_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]