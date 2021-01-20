# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import AddressEnrichment, AddressEnrichmentSl


@admin.register(AddressEnrichment)
class AddressEnrichmentAdmin(admin.ModelAdmin):
    list_display = ["customer", "buy_medium_price", "rent_medium_price"]
    pass


@admin.register(AddressEnrichmentSl)
class AddressEnrichmentSlAdmin(admin.ModelAdmin):
    list_display = ["customer", "label", "cp", "summary_prices_med", "nbHabitants", "nbLogements"]
    pass
