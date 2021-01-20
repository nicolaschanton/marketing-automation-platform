# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from .models import ScriptExecution


@admin.register(ScriptExecution)
class ScriptExecutionAdmin(admin.ModelAdmin):
    list_filter = ["script_name", "created_date"]
    list_display = ["script_name", "status", "created_date"]
    pass
