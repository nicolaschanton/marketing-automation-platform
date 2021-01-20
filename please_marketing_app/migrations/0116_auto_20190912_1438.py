# Generated by Django 2.2.5 on 2019-09-12 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0115_customer_sharable_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='neighborhood',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='neighborhood',
            name='open_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]