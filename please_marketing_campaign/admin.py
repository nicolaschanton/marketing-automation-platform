# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import NotificationCampaign, SmsCampaign, MerchantLaunchCampaign, CronCampaign
from please_marketing_app.models import Neighborhood, Merchant
from django import forms


class NeighborhoodForm(forms.ModelForm):
    neighborhoods = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Neighborhood.objects.all()
    )


class SearchMerchantForm(forms.ModelForm):
    merchant = forms.ModelChoiceField(
        queryset=Merchant.objects.filter().order_by("name"),
    )


@admin.register(NotificationCampaign)
class NotificationCampaignAdmin(admin.ModelAdmin):
    list_filter = ["campaign_sent", "campaign_name"]
    list_display = ["campaign_name", "notification_content_a", "notification_content_b", "test",
                    "campaign_send_date_time", "campaign_sent", "campaign_is_sending", "created_date", "modified_date"]
    form = NeighborhoodForm
    pass


@admin.register(SmsCampaign)
class SmsCampaignAdmin(admin.ModelAdmin):
    list_filter = ["campaign_sent", "campaign_name"]
    list_display = ["campaign_name", "sms_content_a", "sms_content_b", "test",
                    "campaign_send_date_time", "campaign_sent", "campaign_is_sending", "created_date", "modified_date"]
    form = NeighborhoodForm
    pass


@admin.register(MerchantLaunchCampaign)
class MerchantLaunchCampaignAdmin(admin.ModelAdmin):
    search_fields = ["merchant__name"]
    list_filter = ["campaign_sent", "merchant__neighborhood"]
    list_display = ["merchant", "test", "campaign_sent", "campaign_is_sending", "campaign_send_date_time",
                    "created_date", "modified_date"]
    form = SearchMerchantForm
    pass


@admin.register(CronCampaign)
class CronCampaignAdmin(admin.ModelAdmin):
    list_filter = ["active"]
    list_display = ["campaign_name", "script_target", "campaign_is_sending", "campaign_send_time",
                    "created_date", "modified_date"]
    form = NeighborhoodForm
    pass
