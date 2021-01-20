# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import ReferralLead, ReferralMatch


@admin.register(ReferralMatch)
class ReferralMatchAdmin(admin.ModelAdmin):
    search_fields = ["referrer"]
    list_display = ["referrer", "referee", "sms", "created_date", "modified_date"]
    list_display_links = None
    pass


@admin.register(ReferralLead)
class ReferralLeadAdmin(admin.ModelAdmin):
    search_fields = ["referrer"]
    list_display = ["referrer", "lead_email", "lead_sms", "created_date", "modified_date"]
    list_display_links = None
    pass

