# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, IntercomEvent, NotificationHistory, Order, NetPromoterScore, SmsHistory, DeliveryMan, CityManager
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
from .utilities import get_short_url_comment_request
from please_marketing_script_execution.log_script import log_script
from concurrent.futures import ThreadPoolExecutor
from please_marketing_app.main_scripts.utilities import get_good_sender, has_not_received_too_many_communications


# from please_marketing_app.main_scripts.comment_request import *
# customer = Customer.objects.get(email="nicolas.chanton@gmail.com")
def send_comment_request_nps_fan(customer_id):

    customer = Customer.objects.get(id=customer_id.get("customer"))

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    if SmsHistory.objects.filter(customer=customer, sms_type="send_comment_request_store").count() == 0:
        if has_not_received_too_many_communications(customer=customer):

            if IntercomEvent.objects.filter(customer=customer, channel="app").order_by("-created_at").first().os_platform == "iOS":
                link = get_short_url_comment_request(medium="app_store")

            elif IntercomEvent.objects.filter(customer=customer, channel="app").order_by("-created_at").first().os_platform == "Android":
                link = get_short_url_comment_request(medium="play_store")

            else:
                link = "https://goo.gl/AQigfu"

            try:
                message = client.messages.create(
                    str(customer.phone),
                    body=str(
                        "Bonjour "
                        + str(customer.first_name)
                        + ", aujourd'hui on a besoin de vous pour faire grandir Please ! "
                          "Pour nous donner un petit coup de pouce, n'hésitez pas à nous laisser un avis sur les stores ! "
                        + emoji.emojize(u':blush:', use_aliases=True)
                        + str("\n")
                        + str("Merci merci !")
                        + str("\n")
                        + str(link)
                    ),
                    from_=get_good_sender(customer=customer)
                )

                print(message.sid, message.date_created.date, message.body)

                print("SUCCES: SMS properly sent for send_comment_request_nps_fan to user " + customer.email + " - " + customer.phone)

                SmsHistory(
                    customer=customer,
                    content=message.body,
                    send_date=datetime.now(),
                    sms_type="send_comment_request_store",
                ).save()

            except:
                print("ERROR: Twilio API Error - Message for send_comment_request_nps_fan not sent to user " + str(
                    customer.email) + str(sys.exc_info()))

    return


def executor_send_comment_request_nps_fan(neighborhoods):
    log_script(name="executor_send_comment_request_nps_fan", status="s")
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(send_comment_request_nps_fan, NetPromoterScore.objects.filter(
            customer__neighborhood__in=neighborhoods,
            score__gte=9, customer__marketing=True,
            customer__archived=False,
            created_date__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s")))).values("customer"))
    log_script(name="executor_send_comment_request_nps_fan", status="d")
    return


def send_comment_request_community():

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    for city_manager in CityManager.objects.filter(sent_comment_request=None, phone__isnull=False):
        try:
            message = client.messages.create(
                str(city_manager.phone),
                body=str(
                    "Bonjour "
                    + str(city_manager.first_name)
                    + ", afin d'améliorer la notoriété de Please sur Internet, peux-tu prendre quelques minutes pour laisser des avis sur la page Facebook PleaseApp, le profil Google Business ainsi que sur les stores (Apple et Android) ? Merci à toi ! Nicolas de Please"
                    + "\n"
                    + "Page Facebook: "
                    + str(get_short_url_comment_request(medium="facebook"))
                    + "\n"
                    + "Apple Store: "
                    + str(get_short_url_comment_request(medium="apple_store"))
                    + "\n"
                    + "Android Store: "
                    + str(get_short_url_comment_request(medium="android_store"))
                ),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            print("SUCCES: SMS properly sent for send_comment_request_facebook_community to city_manager " + city_manager.email + " - " + city_manager.phone)

            city_manager.sent_comment_request = True
            city_manager.save()

        except:
            print("ERROR: Twilio API Error - Message for send_comment_request_facebook_community to city_manager " + str(city_manager.email) + str(sys.exc_info()))

    for delivery_man in DeliveryMan.objects.filter(sent_comment_request=None, phone__isnull=False):
        try:
            message = client.messages.create(
                str(delivery_man.phone),
                body=str(
                    "Bonjour "
                    + str(delivery_man.first_name)
                    + ", afin d'améliorer la notoriété de Please sur Internet, peux-tu prendre quelques minutes pour laisser des avis sur la page Facebook PleaseApp ainsi que sur les stores (Apple et Android) ? Merci à toi ! Nicolas de Please"
                    + "\n"
                    + "Page Facebook: "
                    + str(get_short_url_comment_request(medium="facebook"))
                    + "\n"
                    + "Apple Store: "
                    + str(get_short_url_comment_request(medium="apple_store"))
                    + "\n"
                    + "Android Store: "
                    + str(get_short_url_comment_request(medium="android_store"))
                ),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            print("SUCCES: SMS properly sent for send_comment_request_community to delivery_man " + delivery_man.email + " - " + delivery_man.phone)

            delivery_man.sent_comment_request = True
            delivery_man.save()

        except:
            print("ERROR: Twilio API Error - Message for send_comment_request_community to delivery_man " + str(delivery_man.email) + str(sys.exc_info()))

    return
