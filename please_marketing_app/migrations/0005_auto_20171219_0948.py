# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-19 09:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0004_intercomevent_order_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Neighborhood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('odoo_id', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='email',
        ),
        migrations.AddField(
            model_name='customer',
            name='odoo_user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='odoo_user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='neighborhood',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='please_marketing_app.Neighborhood'),
        ),
        migrations.AlterField(
            model_name='order',
            name='odoo_order_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='odoo_order_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='odoo_order_line_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
