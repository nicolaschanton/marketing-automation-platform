# Generated by Django 2.0.3 on 2018-05-08 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0036_auto_20180503_0815'),
    ]

    operations = [
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('first_notif_sent', models.BooleanField(default=False)),
                ('first_notif_date', models.DateTimeField(blank=True, null=True)),
                ('first_notif_voucher_code', models.CharField(blank=True, max_length=5, null=True)),
                ('discovery_notif_sent', models.BooleanField(default=False)),
                ('discovery_notif_date', models.DateTimeField(blank=True, null=True)),
                ('discovery_notif_voucher_code', models.CharField(blank=True, max_length=5, null=True)),
                ('neighborhood', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='please_marketing_app.Neighborhood')),
            ],
        ),
    ]