# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, IntercomEvent, NotificationHistory, Order, NetPromoterScore, SmsHistory
from twilio.rest import Client
from datetime import datetime, timedelta
from django.conf import settings
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
import time
from please_marketing_app.get_vouchers.get_voucher import get_one_voucher


def first_notif_merchant():
    for merchant in Merchant.objects.filter(notif_to_be_sent=True, notif_sent=False, rediscover=False, notif_date=datetime.today().date()):
        for customer in Customer.objects.filter(neighborhood=merchant.neighborhood, first_name__isnull=False, marketing=True, archived=False):

            try:
                message_variations = (

                    # Variation 1
                    str("[OUVERTURE ")
                    + str(merchant.type.upper())
                    + emoji.emojize(u':sparkles:', use_aliases=True)
                    + str("] ")
                    + str(merchant.name)
                    + str("\n")
                    + str(customer.first_name)
                    + str(", venez découvrir ce nouveau commerçant dans Please dès maintenant !"),

                    # Variation 2
                    str("[OUVERTURE ")
                    + str(merchant.type.upper())
                    + emoji.emojize(u':sparkles:', use_aliases=True)
                    + str("] ")
                    + str(merchant.name)
                    + str("\n")
                    + str("Disponible dès à présent sur Please !"),

                    # Variation 3
                    str("[OUVERTURE ")
                    + str(merchant.type.upper())
                    + emoji.emojize(u':sparkles:', use_aliases=True)
                    + str("]")
                    + str("\n")
                    + str(customer.first_name)
                    + str(", testez ")
                    + str(merchant.name)
                    + str(" dès maintenant avec Please !"),
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

                print("SUCCESS: new merchant notification properly sent to user " + str(customer.email))
                print(customer.first_name, customer.last_name, message_target)
                print(response.text)

                NotificationHistory(
                    customer=customer,
                    title="Discover Merchant Notification",
                    content=message_target,
                    abandoned_cart=False,
                    abandoned_sign_up=False,
                    rediscover=False,
                    discover=True,
                ).save()

            except:
                print("ERROR: Failed to send new merchant notification for user " + str(customer.email) + " - " + str(
                    sys.exc_info()))

        merchant.notif_sent = True
        merchant.notif_to_be_sent = False
        merchant.save()

    return


def rediscover_notif_merchant():
    for merchant in Merchant.objects.filter(notif_to_be_sent=True, notif_sent=False, rediscover=True, notif_date=datetime.today().date()):
        for customer in Customer.objects.filter(neighborhood=merchant.neighborhood, first_name__isnull=False, marketing=True, archived=False):

            try:
                message_variations = (

                    # Variation 1
                    str("[DÉCOUVERTE ")
                    + str(merchant.type.upper())
                    + emoji.emojize(u':sparkles:', use_aliases=True)
                    + str("]")
                    + str("\n")
                    + str(customer.first_name)
                    + str(", aujourd'hui, découvrez ou redécouvrez ")
                    + str(merchant.name)
                    + str(" dans Please !"),

                    # Variation 2
                    str("[DÉCOUVERTE ")
                    + str(merchant.type.upper())
                    + emoji.emojize(u':sparkles:', use_aliases=True)
                    + str("]")
                    + str("\n")
                    + str(customer.first_name)
                    + str(", ")
                    + str(merchant.name)
                    + str(" est disponible en livraison grâce à Please !"),
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

                print("SUCCESS: rediscovert merchant notification properly sent to user " + str(customer.email))
                print(customer.first_name, customer.last_name, message_target)
                print(response.text)

                NotificationHistory(
                    customer=customer,
                    title="Rediscover Merchant Notification",
                    content=message_target,
                    abandoned_cart=False,
                    abandoned_sign_up=False,
                    rediscover=True,
                    discover=False,
                ).save()

            except:
                print("ERROR: Failed to send rediscover merchant notification for user " + str(customer.email) + " - " + str(
                    sys.exc_info()))

        merchant.notif_sent = True
        merchant.notif_to_be_sent = False
        merchant.save()

    return
