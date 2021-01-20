# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import Merchant


# Create your models here.
class MerchantPictureSource(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    unsplash_id = models.CharField(max_length=100, blank=True, null=True)
    query = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    picture_tags = ArrayField(models.CharField(max_length=25, null=True, blank=True), null=True, blank=True)
    match_type = models.CharField(max_length=2, default='rm', choices=(
        ('sm', 'Safe Match'),
        ('rm', 'Risky Match'),
    ))
    ranking_search = models.IntegerField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.unsplash_id

