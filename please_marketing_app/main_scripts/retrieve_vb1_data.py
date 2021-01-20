# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, IntercomEvent, Neighborhood
import requests
import datetime
from pytz import timezone
import sys
from django.conf import settings
import json
from concurrent.futures import ThreadPoolExecutor
from please_marketing_script_execution.log_script import log_script


def retrieve_vb1(event):

    try:

        viewed_offer = IntercomEvent.objects.filter(customer=event.customer, event_name="viewed offer", created_at__lte=event.created_at).latest("created_at")

        event.universe_name = viewed_offer.universe_name
        event.mw_universe_id = viewed_offer.mw_universe_id
        event.offer_name = viewed_offer.offer_name
        event.mw_offer_id = viewed_offer.mw_offer_id

        event.save()

        print("SUCCESS: Data from Viewed Offer retrieved for event " + str(event.intercom_id))

    except:
        print("ERROR: Data from Viewed Offer not retrieved for event " + str(event.intercom_id) + str(
            sys.exc_info()))

    return


def retrieve_vb1_all(event):

    print(event)

    try:
        viewed_offer = IntercomEvent.objects.filter(customer=event.customer, event_name="viewed offer", created_at__lte=event.created_at).latest("created_at")

        event.universe_name = viewed_offer.universe_name
        event.mw_universe_id = viewed_offer.mw_universe_id
        event.offer_name = viewed_offer.offer_name
        event.mw_offer_id = viewed_offer.mw_offer_id

        event.save()

        print("SUCCESS: Data from Viewed Offer retrieved for event " + str(event.intercom_id))

    except:
        print("ERROR: Data from Viewed Offer not retrieved for event " + str(event.intercom_id) + str(
            sys.exc_info()))

    return


def executor_retrieve_vb1_all():
    log_script(name="executor_retrieve_vb1_all", status="s")

    with ThreadPoolExecutor(max_workers=25) as executor:
        executor.map(retrieve_vb1_all, IntercomEvent.objects.filter(event_name="validated basket 1"))

    log_script(name="executor_retrieve_vb1_all", status="d")
    return

