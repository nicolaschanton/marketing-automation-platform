# Generated by Django 2.2.5 on 2020-04-21 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0116_auto_20190912_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neighborhood',
            name='is_open',
            field=models.NullBooleanField(default=True),
        ),
    ]
