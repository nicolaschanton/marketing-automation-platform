# Generated by Django 2.0.3 on 2019-01-04 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('please_marketing_campaign', '0004_notificationcampaign_campaign_is_sending'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationcampaign',
            name='campaign_is_sending',
            field=models.BooleanField(default=False, help_text='NE PAS TOUCHER'),
        ),
        migrations.AlterField(
            model_name='notificationcampaign',
            name='campaign_name',
            field=models.CharField(blank=True, help_text='Nommer la campagne', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='notificationcampaign',
            name='campaign_sent',
            field=models.BooleanField(default=False, help_text='NE PAS TOUCHER'),
        ),
        migrations.AlterField(
            model_name='notificationcampaign',
            name='notification_content_a',
            field=models.TextField(blank=True, help_text='A REMPLIR OBLIGATOIREMENT - Liste des tags : [first_name], [last_name], [emoji.short_code.emoji] Exemple => [emoji.heart_eyes.emoji]', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='notificationcampaign',
            name='notification_content_b',
            field=models.TextField(blank=True, help_text='A REMPLIR OBLIGATOIREMENT - Liste des tags : [first_name], [last_name], [emoji.short_code.emoji] Exemple => [emoji.heart_eyes.emoji]', max_length=200, null=True),
        ),
    ]
