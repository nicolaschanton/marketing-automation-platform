# Generated by Django 2.0.3 on 2019-03-04 17:53

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_landing_pages', '0002_auto_20190222_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpageimage',
            name='image_file',
            field=cloudinary.models.CloudinaryField(default='', max_length=255, verbose_name='image'),
            preserve_default=False,
        ),
    ]