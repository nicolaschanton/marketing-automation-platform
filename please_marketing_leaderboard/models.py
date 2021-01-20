# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import CityManager


class LeaderboardVoucherCityManager(models.Model):
    city_manager = models.ForeignKey(CityManager, on_delete=models.DO_NOTHING)
    end_of_period_date = models.DateField(max_length=500, null=True, blank=True)
    counter = models.IntegerField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.city_manager.first_name + self.city_manager.last_name
