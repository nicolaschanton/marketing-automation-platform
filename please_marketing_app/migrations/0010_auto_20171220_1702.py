# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-20 17:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0009_auto_20171220_1306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='voucher_order_1',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='voucher_order_2',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='voucher_order_3',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='voucher_order_4',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='voucher_order_5',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_neighborhood',
        ),
        migrations.AddField(
            model_name='order',
            name='neighborhood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='please_marketing_app.Neighborhood'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='city',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='first_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='gender',
            field=models.CharField(blank=True, default=False, max_length=500),
        ),
        migrations.AlterField(
            model_name='customer',
            name='intercom_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_seen_ip',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='profile_picture',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='social_profiles',
            field=models.CharField(blank=True, max_length=100000, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='street',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user_agent_data',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='zip',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='neighborhood',
            name='name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='click_and_collect',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='comments',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='street',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='supplier',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='universe',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='zip',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
