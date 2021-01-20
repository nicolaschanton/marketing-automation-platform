# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import LeaderboardVoucherCityManager


@admin.register(LeaderboardVoucherCityManager)
class LeaderboardVoucherCityManagerAdmin(admin.ModelAdmin):
    list_filter = ["end_of_period_date"]
    list_display = ["city_manager", "counter", "score", "end_of_period_date"]
    pass
