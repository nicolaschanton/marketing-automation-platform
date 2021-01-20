# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, IntercomEvent, Neighborhood, NetPromoterScore
import requests
import datetime
from pytz import timezone
import sys
from django.conf import settings
from django.db.models import Count
import json
from please_marketing_script_execution.log_script import log_script


def deduplicate_events():
    log_script(name="deduplicate_events", status="s")

    duplicates = IntercomEvent.objects.values("intercom_id").annotate(Count("intercom_id")).filter(intercom_id__count__gt=1)

    for event in duplicates:
        print(event.get("intercom_id"))
        IntercomEvent.objects.filter(intercom_id=event.get("intercom_id")).first().delete()

    log_script(name="deduplicate_events", status="d")
    return


def deduplicate_nps():
    log_script(name="deduplicate_nps", status="s")

    for nps in NetPromoterScore.objects.filter():
        count = NetPromoterScore.objects.filter(customer=nps.customer).count()

        if count > 1:
            NetPromoterScore.objects.filter(customer=nps.customer).delete()
        else:
            continue

    log_script(name="deduplicate_nps", status="d")
    return
