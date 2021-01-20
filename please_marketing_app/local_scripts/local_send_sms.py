# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, SmsHistory, IntercomEvent
from twilio.rest import Client
import datetime
from django.conf import settings
from django.db.models import Q
import sys
from concurrent.futures import ThreadPoolExecutor
import emoji


def local_send_sms(customer):

    if SmsHistory.objects.filter(customer=customer, sms_type="Campaign - BLACKFRIDAY 2018").count() == 0:

        # Your Account Sid and Auth Token from twilio.com/user/account
        account_sid = str(settings.TWILIO_SID)
        auth_token = str(settings.TWILIO_TOKEN)
        client = Client(account_sid, auth_token)
        from_phone = str(settings.TWILIO_PHONE)

        print("CURRENT CUSTOMER IS: " + customer.email + " - " + customer.phone)

        try:
            message = client.messages.create(
                str("+33" + customer.phone.lstrip("0")),
                body=str(
                    emoji.emojize(u':hamburger:', use_aliases=True)
                    + emoji.emojize(u':gift:', use_aliases=True)
                    + str(" ")
                    + str("-25% jusqu'à ce soir code HAPPY18 ! ")
                    + str("https://goo.gl/9jq2Tx")),
                from_=from_phone
            )

            print("SUCCESS: SMS properly sent to user ", customer.id, message.sid, message.date_created.date, message.body)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.datetime.now(),
                sms_type="Campaign - HAPPY18"
            ).save()

        except:
            print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


# from please_marketing_app.local_scripts.local_send_sms import *
def executor_send_local_sms_campaign():
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(local_send_sms, Customer.objects.filter(test_user=True, marketing=True, archived=False))

    return
