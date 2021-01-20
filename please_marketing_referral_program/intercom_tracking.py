# -*- coding: utf-8 -*-

import requests
import datetime
from pytz import timezone
import sys
from django.conf import settings
import json


def track_event(event_name, customer, metadata):
    try:

        url = "https://api.intercom.io/events"

        # METADATA FORMAT
        # metadata = {
        #    "data": "data",
        # }

        payload = {
            "event_name": event_name,
            "created_at": datetime.datetime.now().strftime("%s"),
            "user_id": customer.email if not customer.user_id else customer.user_id,
            "metadata": metadata,
        }

        print(payload)

        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': str(settings.INTERCOM_KEY),
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        print(response)

    except:
        print(str("ERROR: " + str(customer.email) + " hasn't been uptaded to Intercom DB - " + str(sys.exc_info())))

    return
