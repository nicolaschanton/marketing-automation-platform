# coding: utf-8

from please_marketing_app.models import Customer, SmsHistory
from twilio.rest import Client
from django.conf import settings
from datetime import datetime
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
import time
from please_marketing_app.main_scripts.utilities import get_good_sender


# from please_marketing_app.main_scripts.send_sms import *
def send_sms(customer, body, sms_type):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            str(customer.phone),
            body=str(body),
            from_=get_good_sender(customer=customer)
        )

        print(message.sid, message.date_created.date, message.body)

        print("SUCCES: SMS properly sent to user " + customer.email + " - " + customer.phone)

        SmsHistory(
            customer=customer,
            content=message.body,
            send_date=datetime.now(),
            sms_type=str(sms_type)
        ).save()

    except:
        try:
            country_code = str(
                SmsHistory.objects.filter(
                    customer__neighborhood=customer.neighborhood,
                    customer__phone__isnull=False
                ).order_by("-send_date").first.customer.phone[:-9]
            )

            message = client.messages.create(
                str(country_code + customer.phone[-9:]),
                body=str(body),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            print("SUCCES: SMS properly sent to user " + customer.email + " - " + customer.phone)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.now(),
                sms_type=str(sms_type)
            ).save()

            # Update customer phone with good country code
            customer.phone = str(country_code + customer.phone[-9:])
            customer.save()

        except:
            print("ERROR: Twilio API Error - SMS not sent to user " + str(customer.email) + str(sys.exc_info()))

    return
