# coding: utf-8

from please_marketing_app.models import Customer, SmsHistory, Order
from please_marketing_app.get_vouchers.get_voucher_next import get_one_voucher
from django.conf import settings
import emoji
import random
import requests
import json
from django.db.models import Q
from twilio.rest import Client
import sys
from concurrent.futures import ThreadPoolExecutor
import datetime
from please_marketing_script_execution.log_script import log_script


# from please_marketing_app.promo_campaigns.one_book_one_voucher import *
# target voucher code = "NEXTLIV"
def one_book_one_voucher(order):
    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    customer = order.customer

    if SmsHistory.objects.filter(customer=customer, sms_type="one_book_one_voucher_NEXTLIV").count() == 0:

        voucher_code = get_one_voucher(
            customer=customer,
            notification_type="one_book_one_voucher_NEXTLIV",
            voucher_name="Coupon 5€ - NEXTLIV",
            voucher_val_type='amount',
            voucher_code=0,
            voucher_value=5,
            voucher_validity=7,
            first_order_only=True,
            first_customer_order=False,
            pricelist_id=False,
            minimum_cart_amount=15,
        )[1]

        try:
            message = client.messages.create(
                str(customer.phone),
                body=str(customer.first_name + ", grâce à votre commande chez " + str(order.supplier_name) + " vous venez de gagner 5€ avec le code " + (str(voucher_code)) + " valable pendant 7j " + emoji.emojize(u':gift:', use_aliases=True) + " !"),
                from_=from_phone
            )

            print("SUCCESS: SMS properly sent for NEXTLIV campaign to user ", customer.id, message.sid, message.date_created.date, message.body)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.datetime.now(),
                sms_type="one_book_one_voucher_NEXTLIV"
            ).save()

        except:
            print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def executor_one_book_one_voucher():
    log_script(name="executor_one_book_one_voucher", status="s")
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(one_book_one_voucher, Order.objects.filter(odoo_order_state='done', voucher_code="NEXTLIV", order_date__gte=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%s")))))
    log_script(name="executor_one_book_one_voucher", status="d")
    return
