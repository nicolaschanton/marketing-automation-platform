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
from please_marketing_app.main_scripts.utilities import get_good_sender, has_not_received_too_many_communications


# from please_marketing_app.main_scripts.nps import *
def send_nps(neighborhoods):
    log_script(name="send_nps", status="s")

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    customers = Order.objects.filter(
        customer__neighborhood__in=neighborhoods,
        customer__isnull=False,
        odoo_order_state="done",
        customer__marketing=True,
        customer__archived=False).values("customer").distinct().order_by("?")[:100]

    for customer_id in customers:
        try:
            customer = Customer.objects.get(id=customer_id.get("customer"))

            if (NetPromoterScore.objects.filter(customer=customer).count() == 0) \
                    and has_not_received_too_many_communications(customer=customer) \
                    and (Order.objects.filter(customer=customer, odoo_order_state="done").count() > 1) \
                    and (Order.objects.filter(customer=customer, odoo_order_state="done", order_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s")))).count() > 0) \
                    and (SmsHistory.objects.filter(customer=customer, sms_type="NPS Monthly Campaign", send_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(days=360)).strftime("%s")))).count() == 0):

                url_nps = "https://pro.pleaseapp.com/nps?id=" + str(customer.id)

                message = client.messages.create(
                    str(customer.phone),
                    body=str(
                        "Bonjour "
                        + str(customer.first_name)
                        + ", vous avez récemment passé commande chez Please ! "
                          "On voulait savoir comment ça s'était passé "
                        + emoji.emojize(u':blush:', use_aliases=True)
                        + "\n"
                        + "Pour répondre et gagner un bon de 5€, c'est par ici : "
                        + str(url_nps)
                    ),
                    from_=get_good_sender(customer=customer)
                )

                print(message.sid, message.date_created.date, message.body)

                print("SUCCES: SMS properly sent for NPS to user " + customer.email + " - " + customer.phone)

                SmsHistory(
                    customer=customer,
                    content=message.body,
                    send_date=datetime.now(),
                    sms_type="NPS Monthly Campaign",
                ).save()

        except:
            print("ERROR: Twilio API Error - Message for NPS not sent to user " + str(customer_id) + str(sys.exc_info()))

    log_script(name="send_nps", status="d")
    return


def send_voucher_nps(customer, score):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    if int(score) >= 5:

        try:
            message = client.messages.create(
                str(customer.phone),
                body=str(
                    str(customer.first_name)
                    + ", merci pour votre réponse, 5€ offerts sur votre prochaine commande avec le code COOL5 "
                    + emoji.emojize(u':gift:', use_aliases=True)
                    + str("!")
                ),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            print("SUCCES: SMS properly sent for NPS to user " + customer.email + " - " + customer.phone)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.now(),
                sms_type="NPS Answer Campaign COOL5",
            ).save()

        except (KeyError, AttributeError):
            print("ERROR: Twilio API Error - Message for NPS not sent")

    elif int(score) < 5:
        try:
            message = client.messages.create(
                str(customer.phone),
                body=str(
                    str(customer.first_name)
                    + ", merci pour votre réponse, apparemment vous avez rencontré des difficultés avec Please. "
                      "Pour nous faire pardonner, on vous offre 10€ sur votre prochaine commande avec le code SORRY "
                    + emoji.emojize(u':gift:', use_aliases=True)
                    + str("!")
                    + str("\n")
                    + str("N'hésitez pas à me contacter à cette adresse pour me faire part de vos difficultés : nicolas@pleaseapp.com")
                    + str("\n")
                    + str("Nicolas @Please")
                ),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            print("SUCCES: SMS properly sent for NPS to user " + customer.email + " - " + customer.phone)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.now(),
                sms_type="NPS Answer Campaign SORRY",
            ).save()

        except (KeyError, AttributeError):
            print("ERROR: Twilio API Error - Message for NPS not sent")

    return
