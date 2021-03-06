# Generated by Django 2.0.3 on 2018-06-05 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0058_notificationhistory_vouchercode'),
    ]

    operations = [
        migrations.AddField(
            model_name='vouchercode',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='vouchercode',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='vouchercode',
            name='sent',
            field=models.NullBooleanField(),
        ),
    ]
