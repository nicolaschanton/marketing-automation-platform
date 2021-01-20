# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField
from please_marketing_app.models import Neighborhood, Merchant, Customer
from cloudinary.models import CloudinaryField


class Lead(models.Model):

    # Lead related fields
    email = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    raw_address = models.CharField(max_length=150, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=5, blank=True, null=True)

    # Tracking related fields
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True, on_delete=models.DO_NOTHING)
    img_name = models.CharField(max_length=200, blank=True, null=True)
    txt_name = models.CharField(max_length=200, blank=True, null=True)
    search_term = models.CharField(max_length=200, blank=True, null=True)

    # Please related fields
    signed_up_please = models.BooleanField(default=False)
    odoo_user_id = models.IntegerField(blank=True, null=True)

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.email


class LandingPageImage(models.Model):
    target_page = models.CharField(max_length=10, default='lp', choices=(
        ('lpa', 'Landing Page Alert'),
        ('lpad', 'Landing Page Alert Done'),
        ('lps', 'Landing Page Signup'),
        ('lp', 'Landing Page'),
    ))
    image_name = models.CharField(max_length=100, blank=True, null=True)
    image_type = models.CharField(max_length=2, default='hr', choices=(
        ('hr', 'Header'),
    ))
    image_file = CloudinaryField('image')

    def __str__(self):
        return self.image_name


class LandingPageText(models.Model):

    target_page = models.CharField(max_length=10, default='lp', choices=(
        ('lpa', 'Landing Page Alert'),
        ('lpad', 'Landing Page Alert Done'),
        ('lps', 'Landing Page Signup'),
        ('lp', 'Landing Page'),
    ))

    text_name = models.CharField(max_length=100, blank=True, null=True)

    text_type = models.CharField(max_length=2, default='hr', choices=(
        ('hr', 'Header'),
        ('sr', 'Sub Header'),
    ), help_text='"<"span">" text "<"span">" pour mettre du texte en jaune')

    text = models.TextField(max_length=500, default='Lorem Ipsum')

    def __str__(self):
        return self.text_name
