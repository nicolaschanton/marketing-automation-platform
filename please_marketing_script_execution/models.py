# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import ArrayField


class ScriptExecution(models.Model):
    STATUS_CHOICES = (
        ("s", 'Started'),
        ("d", 'Done'),
    )
    script_name = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="s")

    # Auto Timestamp Generation
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.script_name
