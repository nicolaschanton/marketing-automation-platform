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
from please_marketing_script_execution.log_script import log_script
from please_marketing_app.main_scripts.utilities import get_good_sender


def slipping_away_30_60():
    log_script(name="slipping_away_30_60", status="s")

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    customers_id_60 = IntercomEvent.objects.filter(
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s")))
    ).values("customer").distinct()

    customers_id_30 = IntercomEvent.objects.filter(
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s")))
    ).values("customer").distinct()

    ids_30 = []
    ids_60 = []

    for cus_id_30 in customers_id_30:
        ids_30.append(cus_id_30.get("customer"))
    for cus_id_60 in customers_id_60:
        ids_60.append(cus_id_60.get("customer"))

    target_ids_30_60 = ids_60

    for id_30 in ids_30:
        target_ids_30_60.remove(id_30)

    target_customers_30_60 = Customer.objects.filter(id__in=target_ids_30_60, marketing=True, archived=False).order_by("?")[:20]

    print(target_customers_30_60.count())

    for customer in target_customers_30_60:
        if (customer.test_user is True) or (customer.test_user is False):
            if SmsHistory.objects.filter(customer=customer,
                                         send_date__gte=datetime.fromtimestamp(float(
                                                 (datetime.today() - timedelta(days=30)).strftime(
                                                         "%s")))).count() == 0:
                try:
                    res_voucher = get_one_voucher(
                        customer=customer,
                        voucher_name=str("Coupon 5€ SMS SA3060 - " + customer.email),
                        notification_type="slipping_away_30_60",
                        voucher_code=0,
                        first_customer_order=False,
                        first_order_only=True,
                        voucher_value=5,
                        voucher_val_type='amount',
                        pricelist_id=False,
                        voucher_validity=7,
                    )

                    voucher_code = res_voucher[1]

                    message_variations = (

                        # Variation 1
                        str(customer.first_name)
                        + ", on ne vous voit plus "
                        + emoji.emojize(u':cry:', use_aliases=True)
                        + str(" !")
                        + str("\n")
                        + emoji.emojize(u':heart_eyes:', use_aliases=True)
                        + emoji.emojize(u':gift:', use_aliases=True)
                        + str(" Si vous revenez on vous offre 5€ : code " + voucher_code + " !")
                        + str("\n")
                        + str("http://onelink.to/pleaseapp"),

                        # Variation 2
                        str(customer.first_name)
                        + ", un "
                        + emoji.emojize(u':gift:', use_aliases=True)
                        + " dans ce SMS !"
                        + str("\n")
                        + emoji.emojize(u':heart_eyes:', use_aliases=True)
                        + str(" On vous offre 5€ sur vos restaurants préférés avec le code " + voucher_code + " !")
                        + str("\n")
                        + str("http://onelink.to/pleaseapp"),

                        # Variation 3
                        str(customer.first_name)
                        + ", un "
                        + emoji.emojize(u':gift:', use_aliases=True)
                        + " dans ce SMS !"
                        + str("\n")
                        + emoji.emojize(u':heart_eyes:', use_aliases=True)
                        + str(" On vous offre 5€ chez vos commerçants préférés avec le code " + voucher_code + " !")
                        + str("\n")
                        + str("http://onelink.to/pleaseapp"),

                    )

                    message_target = message_variations[int(random.randint(0, len(message_variations) - 1))]

                    message = client.messages.create(
                        str(customer.phone),
                        body=message_target,
                        from_=get_good_sender(customer=customer)
                    )

                    print(message.sid, message.date_created.date, message.body)

                    SmsHistory(
                        customer=customer,
                        content=message.body,
                        send_date=datetime.now(),
                        sms_type="slipping_away_30_60",
                    ).save()

                    print("SUCCES: SMS properly sent for slipping away 30_60 to user " + customer.email + " - " + customer.phone)

                except:
                    print("ERROR: Failed to send slipping away 30_60 SMS for user " + str(
                        customer.email) + " - " + str(
                        sys.exc_info()))
            else:
                print("SUCCESS: slipping away 30_60 SMS not sent because of SMS history for user " + str(
                    customer.email))
        else:
            print("SUCCESS: slipping away 30_60 SMS not sent because not a test user for user " + str(
                customer.email))

    log_script(name="slipping_away_30_60", status="d")
    return


def slipping_away_60_120():
    log_script(name="slipping_away_60_120", status="s")

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    customers_id_120 = IntercomEvent.objects.filter(
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=120)).strftime("%s")))
    ).values("customer").distinct()

    customers_id_60 = IntercomEvent.objects.filter(
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s")))
    ).values("customer").distinct()

    ids_60 = []
    ids_120 = []

    for cus_id_60 in customers_id_60:
        ids_60.append(cus_id_60.get("customer"))
    for cus_id_120 in customers_id_120:
        ids_120.append(cus_id_120.get("customer"))

    target_ids_60_120 = ids_120

    for id_60 in ids_60:
        target_ids_60_120.remove(id_60)

    target_customers_60_120 = Customer.objects.filter(id__in=target_ids_60_120, marketing=True, archived=False).order_by("?")[:20]

    print(target_customers_60_120.count())

    for customer in target_customers_60_120:
        if (customer.test_user is True) or (customer.test_user is False):
            if SmsHistory.objects.filter(customer=customer,
                                         send_date__gte=datetime.fromtimestamp(float(
                                                 (datetime.today() - timedelta(days=30)).strftime(
                                                         "%s")))).count() == 0:

                try:
                    res_voucher = get_one_voucher(
                        customer=customer,
                        voucher_name=str("Coupon 10€ SMS SA60120 - " + customer.email),
                        notification_type="slipping_away_60_120",
                        voucher_code=0,
                        first_customer_order=False,
                        first_order_only=True,
                        voucher_value=10,
                        voucher_val_type='amount',
                        pricelist_id=False,
                        voucher_validity=7,
                    )

                    voucher_code = res_voucher[1]

                    message_variations = (

                        # Variation 1
                        str(customer.first_name)
                        + ", on ne vous voit plus "
                        + emoji.emojize(u':cry:', use_aliases=True)
                        + str(" !")
                        + str("\n")
                        + emoji.emojize(u':heart_eyes:', use_aliases=True)
                        + emoji.emojize(u':gift:', use_aliases=True)
                        + str(" Si vous revenez on vous offre 10€ : code " + voucher_code + " !")
                        + str("\n")
                        + str("http://onelink.to/pleaseapp"),

                        # Variation 2
                        str(customer.first_name)
                        + ", un "
                        + emoji.emojize(u':gift:', use_aliases=True)
                        + " dans ce SMS !"
                        + str("\n")
                        + emoji.emojize(u':heart_eyes:', use_aliases=True)
                        + str(" On vous offre 10€ sur vos restaurants préférés avec le code " + voucher_code + " !")
                        + str("\n")
                        + str("http://onelink.to/pleaseapp"),

                        # Variation 3
                        str(customer.first_name)
                        + ", un "
                        + emoji.emojize(u':gift:', use_aliases=True)
                        + " dans ce SMS !"
                        + str("\n")
                        + emoji.emojize(u':heart_eyes:', use_aliases=True)
                        + str(" On vous offre 10€ chez vos commerçants préférés avec le code " + voucher_code + " !")
                        + str("\n")
                        + str("http://onelink.to/pleaseapp"),

                    )

                    message_target = message_variations[int(random.randint(0, len(message_variations) - 1))]

                    message = client.messages.create(
                        str(customer.phone),
                        body=message_target,
                        from_=get_good_sender(customer=customer)
                    )

                    print(message.sid, message.date_created.date, message.body)

                    SmsHistory(
                        customer=customer,
                        content=message.body,
                        send_date=datetime.now(),
                        sms_type="slipping_away_60_120",
                    ).save()

                    print("SUCCES: SMS properly sent for slipping away 60_120 to user " + customer.email + " - " + customer.phone)

                except:
                    print("ERROR: Failed to send slipping away 60_120 SMS for user " + str(
                        customer.email) + " - " + str(
                        sys.exc_info()))

            else:
                print("SUCCESS: slipping away 60_120 SMS not sent because of SMS history for user " + str(
                    customer.email))
        else:
            print("SUCCESS: slipping away 60_120 SMS not sent because not a test user for user " + str(
                customer.email))

    log_script(name="slipping_away_60_120", status="d")
    return
