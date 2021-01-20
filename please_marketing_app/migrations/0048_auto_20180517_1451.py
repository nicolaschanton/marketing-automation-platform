# Generated by Django 2.0.3 on 2018-05-17 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0047_auto_20180517_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merchant',
            name='discovery_notif_date',
        ),
        migrations.RemoveField(
            model_name='merchant',
            name='discovery_notif_sent',
        ),
        migrations.RemoveField(
            model_name='merchant',
            name='discovery_notif_to_be_sent',
        ),
        migrations.RemoveField(
            model_name='merchant',
            name='discovery_notif_voucher_code',
        ),
        migrations.RemoveField(
            model_name='merchant',
            name='first_notif_voucher_code',
        ),
        migrations.AddField(
            model_name='merchant',
            name='email',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]