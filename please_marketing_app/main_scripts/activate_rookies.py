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
from please_marketing_app.get_vouchers.get_voucher_activate_rookies import get_one_voucher
import pytz
from please_marketing_app.main_scripts.utilities import get_good_sender


# from please_marketing_app.main_scripts.activate_rookies import *
# Send a voucher code -10€ via SMS for user having 0 booking and viewing basket 1
def activate_rookie_amount(customer):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    if ((customer.test_user is True) or (customer.test_user is False)) and (((customer.sign_up_date + timedelta(days=2)) < datetime.now(pytz.timezone("Europe/Paris"))) is True) and ((customer.marketing is True) and (customer.archived is False)):
        if Order.objects.filter(customer=customer, odoo_order_state="done").count() == 0:
            if IntercomEvent.objects.filter(customer=customer, event_name="paid order").count() == 0:
                if SmsHistory.objects.filter(customer=customer, send_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s")))).count() == 0:

                    try:
                        res_voucher = get_one_voucher(
                            customer=customer,
                            voucher_name=str("Coupon 1ère commande SMS - " + customer.email),
                            notification_type="activate_rookie",
                            voucher_code=0,
                            first_customer_order=True,
                            first_order_only=True,
                            voucher_value=5,
                            voucher_val_type='amount',
                            pricelist_id=False,
                            voucher_validity=1,
                            minimum_cart_amount=20,
                        )

                        voucher_code = res_voucher[1]

                        message = client.messages.create(
                            str(customer.phone),
                            body=str(
                                str(customer.first_name)
                                + ", envie de vous faire livrer Please à la maison ? "
                                + str("\n")
                                + str("\n")
                                + emoji.emojize(u':grinning:', use_aliases=True)
                                + emoji.emojize(u':gift:', use_aliases=True)
                                + str(" 5€ offerts pendant 24h avec le code " + voucher_code + " ")
                                + str("!")
                            ),
                            from_=get_good_sender(customer=customer)
                        )

                        print(message.sid, message.date_created.date, message.body)

                        SmsHistory(
                            customer=customer,
                            content=message.body,
                            send_date=datetime.now(),
                            sms_type="activate_rookie",
                        ).save()

                        print("SUCCES: SMS properly sent for activate rookie SMS to user " + customer.email + " - " + customer.phone)

                    except (KeyError, AttributeError):
                        print("ERROR: Twilio API Error - Message for activate rookie SMS not sent")

                else:
                    print("SUCCESS: activate rookie SMS not sent because of Notification Hystory to user " + str(
                        customer.email))
            else:
                print("SUCCESS: activate rookie SMS not sent because of paid order event to user " + str(
                    customer.email))
        else:
            print("SUCCESS: activate rookie SMS not sent because of booking history to user " + str(
                customer.email))
    else:
        print("SUCCESS: activate rookie SMS not sent because of booking history to user " + str(
            customer.email))

    return


# Send a voucher code -25% via SMS for user having 0 booking and viewing basket 1
def activate_rookie_percent(customer):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    if ((customer.test_user is True) or (customer.test_user is False)) and (((customer.sign_up_date + timedelta(days=2)) < datetime.now(pytz.timezone("Europe/Paris"))) is True) and ((customer.marketing is True) and (customer.archived is False)):
        if Order.objects.filter(customer=customer, odoo_order_state="done").count() == 0:
            if IntercomEvent.objects.filter(customer=customer, event_name="paid order").count() == 0:
                if SmsHistory.objects.filter(customer=customer, send_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s")))).count() == 0:

                    try:
                        res_voucher = get_one_voucher(
                            customer=customer,
                            voucher_name=str("Coupon 1ère commande SMS - " + customer.email),
                            notification_type="activate_rookie",
                            voucher_code=0,
                            first_customer_order=True,
                            first_order_only=True,
                            voucher_value=25,
                            voucher_val_type='percent',
                            pricelist_id=False,
                            voucher_validity=1,
                            minimum_cart_amount=0,
                        )

                        voucher_code = res_voucher[1]

                        message = client.messages.create(
                            str(customer.phone),
                            body=str(
                                str(customer.first_name)
                                + ", envie de vous faire livrer Please à la maison ? "
                                + str("\n")
                                + str("\n")
                                + emoji.emojize(u':grinning:', use_aliases=True)
                                + emoji.emojize(u':gift:', use_aliases=True)
                                + str(" -25% sur votre première commande pendant 24h avec le code " + voucher_code + " ")
                                + str("!")
                            ),
                            from_=get_good_sender(customer=customer)
                        )

                        print(message.sid, message.date_created.date, message.body)

                        SmsHistory(
                            customer=customer,
                            content=message.body,
                            send_date=datetime.now(),
                            sms_type="activate_rookie",
                        ).save()

                        print("SUCCES: SMS properly sent for activate rookie SMS to user " + customer.email + " - " + customer.phone)

                    except (KeyError, AttributeError):
                        print("ERROR: Twilio API Error - Message for activate rookie SMS not sent")

                else:
                    print("SUCCESS: activate rookie SMS not sent because of Notification Hystory to user " + str(
                        customer.email))
            else:
                print("SUCCESS: activate rookie SMS not sent because of paid order event to user " + str(
                    customer.email))
        else:
            print("SUCCESS: activate rookie SMS not sent because of booking history to user " + str(
                customer.email))
    else:
        print("SUCCESS: activate rookie SMS not sent because of booking history to user " + str(
            customer.email))

    return
