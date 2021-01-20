# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, IntercomEvent, NotificationHistory, Order, NetPromoterScore, SmsHistory
from twilio.rest import Client
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from django.conf import settings
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
import time
from .utilities import strike_price
from please_marketing_app.get_vouchers.get_voucher import get_one_voucher


def abandoned_cart():

    # TARGET EVENTS
    target_events = IntercomEvent.objects.filter(
        event_name="validated basket 1",
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=240)).strftime("%s"))),
        created_at__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=120)).strftime("%s"))),
        customer__marketing=True,
        customer__archived=False,
    )

    target_customers = target_events.values("customer").distinct()

    # CANCELLER EVENTS
    canceler_events = IntercomEvent.objects.filter(
        event_name="paid order",
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=240)).strftime("%s"))),
        customer__marketing=True,
        customer__archived=False,
    )

    canceled_customers = canceler_events.values("customer").distinct()

    # REAL TIME VALIDATION
    for cus_id in target_customers:
        if cus_id not in canceled_customers:
            customer = Customer.objects.get(id=cus_id.get("customer"))
            event = IntercomEvent.objects.filter(
                customer=customer,
                event_name="validated basket 1",
                created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=240)).strftime("%s"))),
                created_at__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=120)).strftime("%s")))
            ).first()

            # HISTORY AND TEST USER VALIDATION
            notif_counter = NotificationHistory.objects.filter(
                customer=customer,
                abandoned_cart=True,
                created_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=4)).strftime("%s"))),
            ).count()

            sms_counter = SmsHistory.objects.filter(
                customer=customer,
                created_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=2)).strftime("%s"))),
            ).count()

            if (notif_counter == 0) and (sms_counter == 0):

                    # MERCHANT TYPE ROUTING
                    if (("restaurant" in event.universe_name) is True) or (("fast food" in event.universe_name) is True):

                        try:
                            merchant = Merchant.objects.get(mw_offer_id=str(event.mw_offer_id))
                            message_variations = (

                                # Variation 1
                                str("Bonjour ")
                                + str(customer.first_name)
                                + str(", votre panier chez ")
                                + str(merchant.name)
                                + str(" vous attend toujours ! ")
                                + emoji.emojize(u':shopping_cart:', use_aliases=True)
                                + str("\n")
                                + str("Commandez dès maintenant ")
                                + emoji.emojize(u':blush:', use_aliases=True),

                                # Variation 2
                                str("Un petit creux ")
                                + str(customer.first_name)
                                + str(" ? ")
                                + emoji.emojize(u':fork_and_knife_with_plate:', use_aliases=True)
                                + str("\n")
                                + str("Profitez-en pour valider votre panier chez ")
                                + str(merchant.name)
                                + str(" ! ")
                                + emoji.emojize(u':blush:', use_aliases=True),
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
                                title="Abandonned Cart Notification",
                                content=message_target,
                                abandoned_cart=True,
                                abandoned_sign_up=False,
                                rediscover=False,
                                discover=False,
                                send_date=datetime.now(),
                            ).save()

                        except:
                            print("ERROR: Failed to send marketing notification for user " + str(customer.email) + " - " + str(
                                sys.exc_info()))

                    else:

                        try:
                            merchant = Merchant.objects.get(mw_offer_id=str(event.mw_offer_id))
                            message_variations = (

                                # Variation 1
                                str("Bonjour ")
                                + str(customer.first_name)
                                + str(", votre panier chez ")
                                + str(merchant.name)
                                + str(" vous attend toujours ! ")
                                + emoji.emojize(u':shopping_cart:', use_aliases=True)
                                + str("\n")
                                + str("Commandez dès maintenant ")
                                + emoji.emojize(u':blush:', use_aliases=True),

                                # Variation 2
                                str("Bonjour ")
                                + str(customer.first_name)
                                + str(", votre panier chez ")
                                + str(merchant.name)
                                + str(" vous attend toujours ! ")
                                + emoji.emojize(u':shopping_cart:', use_aliases=True)
                                + str("\n")
                                + str("Commandez dès maintenant ")
                                + emoji.emojize(u':blush:', use_aliases=True),
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
                                title="Abandonned Cart Notification",
                                content=message_target,
                                abandoned_cart=True,
                                abandoned_sign_up=False,
                                rediscover=False,
                                discover=False,
                                send_date=datetime.now(),
                            ).save()

                        except:
                            print("ERROR: Failed to send marketing notification for user " + str(customer.email) + " - " + str(
                                sys.exc_info()))

    return


def abandoned_cart_voucher():

    # TARGET EVENTS
    target_events = IntercomEvent.objects.filter(
        event_name="validated basket 1",
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=240)).strftime("%s"))),
        created_at__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=120)).strftime("%s"))),
        customer__marketing=True,
        customer__archived=False,
    )

    target_customers = target_events.values("customer").distinct()

    # CANCELLER EVENTS
    canceler_events = IntercomEvent.objects.filter(
        event_name="paid order",
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=240)).strftime("%s"))),
        customer__marketing=True,
        customer__archived=False,
    )

    canceled_customers = canceler_events.values("customer").distinct()

    # REAL TIME VALIDATION
    for cus_id in target_customers:
        if cus_id not in canceled_customers:
            customer = Customer.objects.get(id=cus_id.get("customer"))
            event = IntercomEvent.objects.filter(
                customer=customer,
                event_name="validated basket 1",
                created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=240)).strftime("%s"))),
                created_at__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=120)).strftime("%s")))
            ).first()

            # HISTORY AND TEST USER VALIDATION
            notif_counter = NotificationHistory.objects.filter(
                customer=customer,
                abandoned_cart=True,
                created_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=4)).strftime("%s"))),
            ).count()

            sms_counter = SmsHistory.objects.filter(
                customer=customer,
                created_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=2)).strftime("%s"))),
            ).count()

            total_voucher = 0 if not customer.total_voucher else customer.total_voucher

            if (notif_counter == 0) and (total_voucher < 20) and (sms_counter == 0):

                    # MERCHANT TYPE ROUTING
                    if (("restaurant" in event.universe_name) is True) or (("fast food" in event.universe_name) is True):

                        try:
                            merchant = Merchant.objects.get(mw_offer_id=str(event.mw_offer_id))

                            res_voucher = get_one_voucher(
                                customer=customer,
                                voucher_name=str("Notification Panier Abandonné " + merchant.name + " - " + customer.email),
                                notification_type="SMS",
                                voucher_code=0,
                                first_customer_order=False,
                                first_order_only=True,
                                voucher_value=5,
                                voucher_val_type='amount',
                                pricelist_id=merchant.odoo_offer_id,
                                voucher_validity=1,
                            )

                            voucher_code = res_voucher[1]

                            message_variations = (

                                # Variation 1
                                str("Bonjour ")
                                + str(customer.first_name)
                                + str(", votre panier chez ")
                                + str(merchant.name)
                                + str(" vous attend toujours ! ")
                                + emoji.emojize(u':shopping_cart:', use_aliases=True)
                                + str("\n")
                                + str("5€ offerts pendant 24h avec le code ")
                                + str(voucher_code)
                                + emoji.emojize(u':gift:', use_aliases=True),

                                # Variation 2
                                str("Un petit creux ")
                                + str(customer.first_name)
                                + str(" ? ")
                                + emoji.emojize(u':fork_and_knife_with_plate:', use_aliases=True)
                                + str("\n")
                                + str("5€ offerts chez ")
                                + str(merchant.name)
                                + str(" pendant 24h avec le code ")
                                + str(voucher_code)
                                + emoji.emojize(u':gift:', use_aliases=True)
                                ,
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
                                title="Abandonned Cart Notification Voucher",
                                content=message_target,
                                abandoned_cart=True,
                                abandoned_sign_up=False,
                                rediscover=False,
                                discover=False,
                                send_date=datetime.now(),
                            ).save()

                        except:
                            print("ERROR: Failed to send marketing notification for user " + str(customer.email) + " - " + str(
                                sys.exc_info()))

                    else:

                        try:
                            merchant = Merchant.objects.get(mw_offer_id=str(event.mw_offer_id))

                            res_voucher = get_one_voucher(
                                customer=customer,
                                voucher_name=str("Notification Panier Abandonné " + merchant.name + " - " + customer.email),
                                notification_type="SMS",
                                voucher_code=0,
                                first_customer_order=False,
                                first_order_only=True,
                                voucher_value=5,
                                voucher_val_type='amount',
                                pricelist_id=merchant.odoo_offer_id,
                                voucher_validity=1,
                            )

                            voucher_code = res_voucher[1]

                            message_variations = (

                                # Variation 1
                                str("Bonjour ")
                                + str(customer.first_name)
                                + str(", votre panier chez ")
                                + str(merchant.name)
                                + str(" vous attend toujours ! ")
                                + emoji.emojize(u':shopping_cart:', use_aliases=True)
                                + str("\n")
                                + str("5€ offerts pendant 24h avec le code ")
                                + str(voucher_code)
                                + emoji.emojize(u':gift:', use_aliases=True),

                                # Variation 2
                                str("Bonjour ")
                                + str(customer.first_name)
                                + str(", votre panier chez ")
                                + str(merchant.name)
                                + str(" vous attend toujours ! ")
                                + emoji.emojize(u':shopping_cart:', use_aliases=True)
                                + str("\n")
                                + str("5€ offerts pendant 24h avec le code ")
                                + str(voucher_code)
                                + emoji.emojize(u':gift:', use_aliases=True),
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
                                title="Abandonned Cart Notification Voucher",
                                content=message_target,
                                abandoned_cart=True,
                                abandoned_sign_up=False,
                                rediscover=False,
                                discover=False,
                                send_date=datetime.now(),
                            ).save()

                        except:
                            print("ERROR: Failed to send marketing notification for user " + str(customer.email) + " - " + str(
                                sys.exc_info()))

    return
