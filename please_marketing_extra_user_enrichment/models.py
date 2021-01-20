# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import Customer


class AddressEnrichment(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)

    buy_low_price = models.FloatField(blank=True, null=True)
    buy_medium_price = models.FloatField(blank=True, null=True)
    buy_high_price = models.FloatField(blank=True, null=True)

    rent_low_price = models.FloatField(blank=True, null=True)
    rent_medium_price = models.FloatField(blank=True, null=True)
    rent_high_price = models.FloatField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class AddressEnrichmentSl(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)

    # Address
    latitude = models.CharField(max_length=150, blank=True, null=True)
    longitude = models.CharField(max_length=150, blank=True, null=True)
    label = models.CharField(max_length=150, blank=True, null=True)
    cp = models.CharField(max_length=150, blank=True, null=True)

    # Prices Buying Average
    summary_prices_max = models.FloatField(blank=True, null=True)
    summary_prices_med = models.FloatField(blank=True, null=True)
    summary_prices_min = models.FloatField(blank=True, null=True)

    # House Market Data
    market_numbers_selling = models.FloatField(blank=True, null=True)
    market_numbers_sold = models.FloatField(blank=True, null=True)
    market_numbers_numberMainResidence = models.FloatField(blank=True, null=True)
    market_numbers_numberSecondaryResidence = models.FloatField(blank=True, null=True)
    market_numbers_numberTotalResidence = models.FloatField(blank=True, null=True)

    # Home Composition
    single = models.IntegerField(blank=True, null=True)
    couple = models.IntegerField(blank=True, null=True)
    family = models.IntegerField(blank=True, null=True)

    # Neighborhood Info
    poi_transport_count = models.IntegerField(blank=True, null=True)
    poi_education_count = models.IntegerField(blank=True, null=True)
    poi_neighbors_count = models.IntegerField(blank=True, null=True)
    poi_hotels_count = models.IntegerField(blank=True, null=True)
    poi_commerces_count = models.IntegerField(blank=True, null=True)

    # Stats INSEE
    nbLogements = models.IntegerField(blank=True, null=True)
    nbHabitants = models.IntegerField(blank=True, null=True)
    peopleDensity = models.IntegerField(blank=True, null=True)
    ageMed = models.IntegerField(blank=True, null=True)
    age25MoinsPcent = models.IntegerField(blank=True, null=True)
    age25PlusPcent = models.IntegerField(blank=True, null=True)
    nbEntreprises = models.IntegerField(blank=True, null=True)
    nbCreationEntreprises = models.IntegerField(blank=True, null=True)
    pcentActifsAll = models.IntegerField(blank=True, null=True)
    pcentActifs30 = models.IntegerField(blank=True, null=True)
    pcentUnemployed = models.IntegerField(blank=True, null=True)
    averageIncome = models.IntegerField(blank=True, null=True)
    pcentEtudiants = models.IntegerField(blank=True, null=True)
    pcentResPrincipales = models.IntegerField(blank=True, null=True)
    pcentResSecondaires = models.IntegerField(blank=True, null=True)
    pcentLogVacants = models.IntegerField(blank=True, null=True)
    pcentLocataires = models.IntegerField(blank=True, null=True)
    pcentPrpriotaires = models.IntegerField(blank=True, null=True)
    pcentAppartement = models.IntegerField(blank=True, null=True)
    pcentMaisons = models.IntegerField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email
