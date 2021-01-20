# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import BaseSiren, Lead, GameVoucher, GameVoucherVernon


@admin.register(BaseSiren)
class BaseSireneAdmin(admin.ModelAdmin):
    search_fields = ["siren", "nom", "enseigne"]
    list_filter = ["libnj"]
    list_display = ["siren", "enseigne"]
    pass


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    search_fields = ["email", "last_name"]
    list_display = ["email", "first_name", "last_name", "phone", "city", "merchant", "signed_up_please", "modified_date", "created_date"]
    pass


@admin.register(GameVoucher)
class GameVoucherAdmin(admin.ModelAdmin):
    search_fields = ["customer"]
    list_display = ["customer", "merchant", "voucher_value"]
    pass


@admin.register(GameVoucherVernon)
class GameVoucherVernonAdmin(admin.ModelAdmin):
    search_fields = ["email"]
    list_display = ["email", "merchant", "voucher_value"]
    pass
