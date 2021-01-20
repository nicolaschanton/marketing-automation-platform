# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import VectorBooking, CosineSimilarityBooking, VectorMerchant


@admin.register(VectorBooking)
class VectorBookingAdmin(admin.ModelAdmin):
    list_display = ["customer", "vector", "vector_merchant"]
    pass


@admin.register(CosineSimilarityBooking)
class CosineSimilarityBookingAdmin(admin.ModelAdmin):
    list_display = ["customer_1", "customer_2", "cos_sim_value"]
    pass


@admin.register(VectorMerchant)
class VectorMerchantAdmin(admin.ModelAdmin):
    list_display = ["neighborhood", "vector"]
    pass
