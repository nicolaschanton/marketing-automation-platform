# Generated by Django 2.0.3 on 2019-06-12 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0106_auto_20190603_1517'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po_vo_ratio', models.FloatField()),
                ('average_rating', models.FloatField()),
                ('average_basket', models.FloatField()),
                ('average_please_amount', models.FloatField()),
                ('average_partner_amount', models.FloatField()),
                ('order_number', models.FloatField()),
                ('trending_orders_30', models.FloatField()),
                ('trending_orders_60', models.FloatField()),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='please_marketing_app.Merchant')),
            ],
        ),
    ]
