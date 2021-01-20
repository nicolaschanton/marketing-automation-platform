# Generated by Django 2.0.3 on 2019-03-31 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_landing_pages', '0006_auto_20190304_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpageimage',
            name='image_type',
            field=models.CharField(choices=[('hr', 'Header')], default='hr', max_length=2),
        ),
        migrations.AlterField(
            model_name='landingpageimage',
            name='target_page',
            field=models.CharField(choices=[('lpa', 'Landing Page Alert'), ('lpad', 'Landing Page Alert Done'), ('lps', 'Landing Page Signup'), ('lp', 'Landing Page')], default='lp', max_length=10),
        ),
        migrations.AlterField(
            model_name='landingpagetext',
            name='target_page',
            field=models.CharField(choices=[('lpa', 'Landing Page Alert'), ('lpad', 'Landing Page Alert Done'), ('lps', 'Landing Page Signup'), ('lp', 'Landing Page')], default='lp', max_length=10),
        ),
        migrations.AlterField(
            model_name='landingpagetext',
            name='text_type',
            field=models.CharField(choices=[('hr', 'Header'), ('sr', 'Sub Header')], default='hr', help_text='"<"span">" text "<"span">" pour mettre du texte en jaune', max_length=2),
        ),
    ]
