# coding: utf-8

from please_marketing_app.models import Customer, NotificationHistory, SmsHistory
from django.conf import settings
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
from concurrent.futures import ThreadPoolExecutor


# from please_marketing_app.local_scripts.local_send_notif import *
def send_notif(customer):
    print("CURRENT CUSTOMER IS: " + customer.email + " - " + customer.phone)

    try:
        message_variations = (

            # Variation 1
            str(
                str("[TARIF UNIQUE")
                + emoji.emojize(u':sparkles:', use_aliases=True)
                + str("] ")
                + str(customer.first_name)
                + str(", la livraison à 2,49€ où que vous soyez !")
            ),

            # Variation 2
            str(
                str("[TARIF UNIQUE")
                + emoji.emojize(u':sparkles:', use_aliases=True)
                + str("] ")
                + str("Livraison à 2,49€ quelque soit la distance entre le restau et chez vous ")
                + emoji.emojize(u':heart_eyes:', use_aliases=True)
            ),
        )

        message_target = message_variations[int(random.randint(0, len(message_variations) - 1))]

        url = "https://mw.please-it.com/next-mw/api/notification/pushnotification"

        headers = {
            'Content-Type': "application/json",
            'Authorization': str(settings.PLEASE_MW_TOKEN),
            'Cache-Control': "no-cache",
        }

        payload_json = json.dumps({
            "notId": "",
            "object_id": 0,
            "object_name": "",
            "destination": "customer",
            "action": "",
            "message": message_target,
            "partnerIds": [customer.odoo_user_id]
        })

        response = requests.request("POST", url, data=payload_json, headers=headers)

        print("SUCCESS: marketing notification properly sent to user " + str(customer.email))
        print(customer.first_name, customer.last_name, message_target)
        print(response.text)

        NotificationHistory(
            customer=customer,
            title="Marketing Campaign Notification - Pau Livraison à 2,49€",
            content=message_target,
            abandoned_cart=False,
            abandoned_sign_up=False,
            rediscover=False,
            discover=False,
        ).save()

    except:
        print("ERROR: Failed to send marketing notification for user " + str(customer.email) + " - " + str(
            sys.exc_info()))

    return


def executor_send_notif():
    with ThreadPoolExecutor(max_workers=25) as executor:
        executor.map(send_notif, Customer.objects.filter(
            #neighborhood__mw_id=305,
            id__in=[8243, 6233],
            test_user=True,
            first_name__isnull=False,
            marketing=True,
            archived=False).exclude(email="krix33@gmail.com"))
    return


#id=8243, 6233
