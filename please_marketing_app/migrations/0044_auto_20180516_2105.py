# Generated by Django 2.0.3 on 2018-05-16 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_app', '0043_fullcontactapi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='sent_to_full_contact_api',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='sent_to_gender_api',
        ),
    ]
