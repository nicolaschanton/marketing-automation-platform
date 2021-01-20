# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, CityManager, Customer
from please_marketing_app.get_vouchers.get_voucher import get_one_voucher
from please_marketing_merchant_campaign.models import MerchantTestLaunchCampaign
import datetime
from twilio.rest import Client
import sys
from django.conf import settings
import requests
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# from please_marketing_merchant_campaign.unavailable_items_campaign import *
def send_unvailabale_items_email(merchant, items):
    try:
        msg = EmailMessage(
            str("Vous avez " + len(items) + " article(s) indisponible(s) dans Please"),
            str(render_to_string('please_marketing_referral_program/email_templates/email_parrainage',
                                 {'merchant': merchant, 'item_list': items})),
            "Please <contact@pleaseapp.com>",
            ["nicolas.chanton@gmail.com"],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        print("SUCCESS: Email for unavailable items properly sent to merchant " + merchant.email)

    except:
        print("ERROR: Email for unavailable items - Message not sent " + " - " + str(sys.exc_info()))

    return


def retrieve_unavailable_items():
    for merchant in Merchant.objects.filter(active=True):
        item_list = []
        url = str("https://mw.please-it.com/next-mw/api/public/website/services/menu/" + str(id))
        response = requests.request("GET", url).json()

        for category in response.get("menuCategories"):
            for item in category.get("articles"):
                print(str(item.get("name")))
                if bool(item.get("unavailable")) is True:
                    print(str(item.get("name")) + " - Unavailable")
                    item_list.append(item.get("name"))

        if len(item_list) > 0:
            send_unvailabale_items_email(merchant=merchant, items=item_list)
    return
