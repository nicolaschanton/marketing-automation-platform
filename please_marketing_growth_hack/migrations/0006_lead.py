# Generated by Django 2.0.3 on 2019-01-25 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_growth_hack', '0005_auto_20181219_2251'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, max_length=150, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
                ('street', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('zip', models.CharField(blank=True, max_length=5, null=True)),
                ('signed_up_please', models.BooleanField(default=False)),
                ('odoo_user_id', models.IntegerField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
