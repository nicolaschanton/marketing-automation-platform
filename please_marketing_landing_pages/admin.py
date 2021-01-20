# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import Lead, LandingPageImage, LandingPageText


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    search_fields = ["email", "last_name", "first_name"]

    list_filter = [
        "signed_up_please",
        "neighborhood",
        "img_name",
        "txt_name",
        "search_term",
    ]

    list_display = [
        "email",
        "first_name",
        "last_name",
        "signed_up_please",
        "neighborhood",
        "img_name",
        "txt_name",
        "search_term",
        "created_date",
        "modified_date"
    ]
    pass


@admin.register(LandingPageImage)
class LandingPageImageAdmin(admin.ModelAdmin):
    search_fields = ["target_page"]
    list_display = [
        "image_name",
        "image_type",
        "image_file",
        "target_page"
    ]

    list_filter = [
        "image_name",
        "target_page",
    ]

    pass


@admin.register(LandingPageText)
class LandingPageTextAdmin(admin.ModelAdmin):
    search_fields = ["target_page"]

    list_display = [
        "text_name",
        "text_type",
        "text",
        "target_page"
    ]

    list_filter = [
        "text_name",
        "target_page",
    ]

    save_as = True
    pass
