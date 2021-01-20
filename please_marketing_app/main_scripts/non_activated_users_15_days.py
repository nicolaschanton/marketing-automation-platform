# coding: utf-8

from please_marketing_app.models import Customer, Order, IntercomEvent, SmsHistory, NotificationHistory
from please_marketing_script_execution.log_script import log_script
from please_marketing_app.get_vouchers.get_voucher_activate_rookies_massive import get_one_voucher
from twilio.rest import Client
from datetime import datetime, timedelta
import sys
from django.conf import settings
import emoji
import random
import requests
import json
from please_marketing_app.main_scripts.utilities import get_good_sender, has_not_received_too_many_communications


# Sending automatic SMS to non activated users +15 days after sign up
# from please_marketing_app.main_scripts.non_activated_users_15_days import *
# from please_marketing_app.models import Customer, Order, SmsHistory
def get_voucher(customer):

    voucher_code = get_one_voucher(
        customer=customer,
        notification_type='launch_non_activated_users_15_days',
        voucher_name='Coupon Première Commande -50%',
        voucher_validity=7,
        voucher_value=50,
        voucher_val_type='percent',
        voucher_code=0,
        first_order_only=True,
        first_customer_order=True,
        pricelist_id=False,
        minimum_cart_amount=0,
        maximum_cart_amount=30
    )[1]

    return voucher_code


def send_sms(customer):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    try:
        voucher_code = get_voucher(customer=customer)

        message_variations = (

            str(
                str("PROMO")
                + emoji.emojize(u':sparkles:', use_aliases=True)
                + str(": -50% sur votre 1ère livraison de restaurant ou commerce (jusqu'à 30€ d'achat) code ")
                + str(voucher_code)
                + str(" (valable 7j) !")
                + str("\n")
                + str("www.pleaseapp.com")
            ),

            str(
                str(customer.first_name)
                + str(", on vous offre -50% sur votre 1ère livraison ")
                + emoji.emojize(u':hamburger:', use_aliases=True)
                + str(" (jusqu'à 30€ d'achat) avec le code ")
                + str(voucher_code)
                + str(" ")
                + emoji.emojize(u':gift:', use_aliases=True)
                + str(" (valable 7j) !")
                + str("\n")
                + str("www.pleaseapp.com")
            ),

            str(
                str(customer.first_name)
                + str(", on vous offre -50% sur votre 1ère livraison ")
                + emoji.emojize(u':heart_eyes:', use_aliases=True)
                + str(" (jusqu'à 30€ d'achat) avec le code ")
                + str(voucher_code)
                + str(" ")
                + emoji.emojize(u':gift:', use_aliases=True)
                + str(" (valable 7j) !")
                + str("\n")
                + str("www.pleaseapp.com")
            )
        )

        message_target = message_variations[int(random.randint(0, len(message_variations) - 1))]

        message = client.messages.create(
            str(customer.phone),
            body=str(message_target),
            from_=get_good_sender(customer=customer)
        )

        print("SUCCESS: SMS properly sent to user ", customer.id, message.sid, message.date_created.date, message.body)

        SmsHistory(
            customer=customer,
            content=message.body,
            send_date=datetime.now(),
            sms_type=str("launch_non_activated_users_15_days")
        ).save()

    except:
       print("ERROR: Failed to send SMS launch_non_activated_users_15_days for user " + str(customer.email) + " - "
             + str(sys.exc_info()))

    return


def launch_non_activated_users_15_days(neighborhoods):
    log_script(name="launch_non_activated_users_15_days", status="s")

    # Exclusion based on SmsHistory, NotificationHistory, IntercomEvent & Order
    # Building a first exclusion list
    exclusion_list_of_customer_id = []

    for sms in SmsHistory.objects.filter(
            sms_type='launch_non_activated_users_15_days',
            customer__neighborhood__in=neighborhoods,
            send_date__gt=datetime.fromtimestamp(
                float((datetime.today() - timedelta(days=365)).strftime("%s")))):

        exclusion_list_of_customer_id.append(sms.customer.id)

    # Filter Sign up Date gt than 15 days
    for customer in Customer.objects.filter(
            neighborhood__in=neighborhoods,
            marketing=True,
            orders_number=0,
            total_spent=0,
            sign_up_date__lt=datetime.fromtimestamp(
                float((datetime.today() - timedelta(days=15)).strftime("%s")))).exclude(id__in=exclusion_list_of_customer_id).order_by('?')[:200]:

        if Order.objects.filter(
                customer=customer,
                odoo_order_state='done').count() == 0:

            if has_not_received_too_many_communications(
                customer=customer
            ):

                if IntercomEvent.objects.filter(
                        customer=customer,
                        event_name='paid_order').count() == 0:

                    send_sms(customer=customer)

    log_script(name="launch_non_activated_users_15_days", status="d")

    return
