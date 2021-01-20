# -*- coding: utf-8 -*-

from django.db import models
from please_marketing_app.models import Neighborhood, Merchant
from django.contrib.postgres.fields import ArrayField


class NotificationCampaign(models.Model):
    campaign_name = models.CharField(max_length=50, help_text="Nommer la campagne")
    notification_content_a = models.TextField(max_length=200, help_text="A REMPLIR OBLIGATOIREMENT - Liste des tags : [first_name], [last_name], [emoji.short_code.emoji] Exemple => [emoji.heart_eyes.emoji]")
    notification_content_b = models.TextField(max_length=200, help_text="A REMPLIR OBLIGATOIREMENT - Liste des tags : [first_name], [last_name], [emoji.short_code.emoji] Exemple => [emoji.heart_eyes.emoji]")
    neighborhoods = models.ManyToManyField(Neighborhood)
    test = models.BooleanField(default=True)
    campaign_send_date_time = models.DateTimeField(blank=True, null=True)
    campaign_is_sending = models.BooleanField(default=False, help_text="NE PAS TOUCHER")
    campaign_sent = models.BooleanField(default=False, help_text="NE PAS TOUCHER")

    max_order_number = models.IntegerField(default=0, help_text="Nombre de commandes maximum effectuées par les users ciblés")
    min_order_number = models.IntegerField(default=0, help_text="Nombre de commandes minimum effectuées par les users ciblés")

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.campaign_name


class SmsCampaign(models.Model):
    campaign_name = models.CharField(max_length=50, help_text="Nommer la campagne")
    sms_content_a = models.TextField(max_length=200, help_text="A REMPLIR OBLIGATOIREMENT - Liste des tags : [first_name], [last_name], [emoji.short_code.emoji] Exemple => [emoji.heart_eyes.emoji]")
    sms_content_b = models.TextField(max_length=200, help_text="A REMPLIR OBLIGATOIREMENT - Liste des tags : [first_name], [last_name], [emoji.short_code.emoji] Exemple => [emoji.heart_eyes.emoji]")
    neighborhoods = models.ManyToManyField(Neighborhood)
    test = models.BooleanField(default=True)
    campaign_send_date_time = models.DateTimeField(blank=True, null=True)
    campaign_is_sending = models.BooleanField(default=False, help_text="NE PAS TOUCHER")
    campaign_sent = models.BooleanField(default=False, help_text="NE PAS TOUCHER")

    max_order_number = models.IntegerField(default=0, help_text="Nombre de commandes maximum effectuées par les users ciblés")
    min_order_number = models.IntegerField(default=0, help_text="Nombre de commandes minimum effectuées par les users ciblés")

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.campaign_name


class MerchantLaunchCampaign(models.Model):
    merchant = models.ForeignKey(Merchant, blank=True, null=True, on_delete=models.DO_NOTHING)
    test = models.BooleanField(default=True)

    campaign_send_date_time = models.DateTimeField(blank=True, null=True)
    campaign_is_sending = models.BooleanField(default=False, help_text="NE PAS TOUCHER")
    campaign_sent = models.BooleanField(default=False, help_text="NE PAS TOUCHER")

    email_image = models.ImageField(upload_to=str('merchant_launch_campaign/email_image/'))

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.merchant.name


class CronCampaign(models.Model):
    SCRIPT_CHOICES = (
        ('RPR', 'Referral Program Remember'),
        ('NPS', 'Net Promoter Score'),
        ('FCR', 'Fan Comment Request'),
        ('LNA', 'Launch Non Activated Users 15 Days'),
    )

    campaign_name = models.CharField(max_length=50, help_text="Nommer la campagne")
    script_target = models.CharField(
        max_length=3,
        choices=SCRIPT_CHOICES,
        default='RPR',
    )
    neighborhoods = models.ManyToManyField(Neighborhood)
    active = models.BooleanField(default=True)

    campaign_send_time = models.TimeField(blank=True, null=True)
    campaign_is_sending = models.BooleanField(default=False, help_text="NE PAS TOUCHER")

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.campaign_name
