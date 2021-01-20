# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import Customer, SmsHistory


class ReferralMatch(models.Model):
    referrer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='referrer')
    referee = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='referee')
    sms = models.ForeignKey(SmsHistory, on_delete=models.DO_NOTHING, blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.referrer.email


class ReferralLead(models.Model):
    referrer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.DO_NOTHING)
    lead_email = models.CharField(max_length=500, null=True, blank=True)
    lead_sms = models.CharField(max_length=500, null=True, blank=True)
    sent_to_intercom = models.BooleanField(default=False)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.referrer.email

