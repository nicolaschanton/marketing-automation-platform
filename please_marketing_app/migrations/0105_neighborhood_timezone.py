# Generated by Django 2.0.3 on 2019-06-03 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0104_auto_20190516_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='neighborhood',
            name='timezone',
            field=models.IntegerField(choices=[(1, 'Europe/Paris'), (2, 'Indian/Reunion')], default=1),
        ),
    ]
