# Generated by Django 2.0.3 on 2019-03-04 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_landing_pages', '0005_auto_20190304_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpagetext',
            name='text_type',
            field=models.CharField(choices=[('hr', 'Header'), ('sr', 'Sub Header'), ('bn', 'Button')], default='hr', help_text='"<"span">" text "<"span">" pour mettre du texte en jaune', max_length=2),
        ),
    ]
