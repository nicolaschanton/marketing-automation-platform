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
from please_marketing_script_execution.log_script import log_script
from please_marketing_app.main_scripts.utilities import get_good_sender


def wish_feast():
    log_script(name="wish_feast", status="s")

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    if Fete.objects.filter(month=datetime.today().month, day=datetime.today().day) is None:
        print("Error - No name found")

    else:

        target_fnames = Fete.objects.filter(month=datetime.today().month, day=datetime.today().day)

        print("TARGET FIRST NAMES ARE: " + str(target_fnames.values()))

        for target_fname in target_fnames:

            for customer in Customer.objects.filter(first_name__iexact=target_fname.first_name, marketing=True, archived=False):

                print("CURRENT CUSTOMER IS: " + customer.email + customer.phone)

                try:

                    message = client.messages.create(
                            str(customer.phone),
                            body=str("Bonjour "
                                     + str(customer.first_name)
                                     + ", aujourd'hui c'est votre fête ! Alors chez Please on voulait vous souhaiter "
                                       "une belle journée. A très vite sur Please (www.pleaseapp.com) !"),
                            from_=get_good_sender(customer=customer)
                    )

                    print(message.sid, message.date_created.date, message.body)

                    print("SUCCES: SMS properly sent for feast to user " + customer.email + " - " + customer.phone)

                    SmsHistory(
                        customer=customer,
                        content=message.body,
                        send_date=datetime.now(),
                        sms_type="Wish Feast"
                    ).save()

                except (KeyError, AttributeError):
                    print("ERROR: Twilio API Error - Message not sent")
                    continue

    log_script(name="wish_feast", status="d")
    return
