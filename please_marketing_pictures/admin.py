# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import MerchantPictureSource


@admin.register(MerchantPictureSource)
class MerchantPictureSourceAdmin(admin.ModelAdmin):
    list_display = ["merchant", "description", "likes", "match_type", "query"]

    raw_id_fields = ('merchant',)
