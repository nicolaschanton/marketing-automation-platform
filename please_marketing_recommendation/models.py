# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import Customer, Merchant, Neighborhood


class VectorMerchant(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True, on_delete=models.DO_NOTHING)
    vector = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.neighborhood.name


class VectorBooking(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    vector_merchant = models.ForeignKey(VectorMerchant, blank=True, null=True, on_delete=models.DO_NOTHING)
    vector = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email


class CosineSimilarityBooking(models.Model):
    customer_1 = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='customer_1')
    customer_2 = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='customer_2')

    cos_sim_value = models.FloatField()

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.customer.email
