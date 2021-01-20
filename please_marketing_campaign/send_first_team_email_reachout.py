# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, Customer, Neighborhood, NotificationHistory
from please_marketing_campaign.models import MerchantLaunchCampaign
from please_marketing_campaign.message_variations import launch_notification_variations, launch_email_subject_variations, launch_email_variations
from datetime import datetime, timedelta
import sys
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
import emoji
import random
import requests
import json
from please_marketing_app.get_vouchers.get_voucher_merchant_launch import get_one_voucher_options
import unicodedata
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# from please_marketing_campaign.send_launch_campaign import *
def send_launch_campaign():

    for launch_campaign in MerchantLaunchCampaign.objects.filter(
            campaign_sent=False,
            campaign_is_sending=False,
            campaign_send_date_time__lte=datetime.fromtimestamp(float((datetime.today()).strftime("%s")))):

        launch_campaign.campaign_is_sending = True
        launch_campaign.save()

        def get_launch_merchant_voucher():
            voucher_code_raw = get_one_voucher_options(
                notification_type='',
                voucher_name=str("Coupon de lancement commerçant - " + str(launch_campaign.merchant.name)),
                voucher_validity=7,
                voucher_value=3,
                voucher_val_type='amount',
                voucher_code=str(unicodedata.normalize('NFD', str(launch_campaign.merchant.name[:10].upper() + str(random.randint(10, 99))).replace(" ", "").replace("-", "").replace("'", "")).encode('ascii', 'ignore').decode('UTF-8')),
                first_order_only=True,
                first_customer_order=False,
                pricelist_id='',
                minimum_cart_amount=15,
                total_available=-1,
            )[0]

            return str(voucher_code_raw)

        voucher_code = get_launch_merchant_voucher()

        def send_launch_notification(customer):

            try:
                message_variations = launch_notification_variations

                message_target = message_variations[int(random.randint(0, len(message_variations) - 1))].replace("@merchant_name", str(launch_campaign.merchant.name))

                url = "https://mw.please-it.com/next-mw/api/notification/pushnotification"

                headers = {
                    'Content-Type': "application/json",
                    'Authorization': str(settings.PLEASE_MW_TOKEN),
                    'Cache-Control': "no-cache",
                }

                payload_json = json.dumps({
                    "notId": "",
                    "object_id": 0,
                    "object_name": "",
                    "destination": "customer",
                    "action": "",
                    "message": message_target,
                    "partnerIds": [customer.odoo_user_id]
                })

                response = requests.request("POST", url, data=payload_json, headers=headers)

                print("SUCCESS: launch merchant campaign notification properly sent to user " + str(customer.email))
                print(customer.first_name, customer.last_name, message_target)
                print(response.text)

                NotificationHistory(
                    customer=customer,
                    title="Marketing Launch Merchant - " + str(launch_campaign.merchant.name),
                    content=message_target,
                    abandoned_cart=False,
                    abandoned_sign_up=False,
                    rediscover=False,
                    discover=False,
                ).save()

            except:
                print("ERROR: Failed to send launch merchant campaign notification for user " + str(customer.email) + " - " + str(
                    sys.exc_info()))

            return

        def send_launch_email(customer):

            try:

                subject_variations = launch_email_subject_variations
                subject_target = subject_variations[int(random.randint(0, len(subject_variations) - 1))].replace(
                    "@first_name", str(customer.first_name)).replace("@merchant_name", str(launch_campaign.merchant.name))

                body_variations = launch_email_variations
                body_target = body_variations[int(random.randint(0, len(body_variations) - 1))].replace(
                    "@first_name", str(customer.first_name)).replace("@merchant_name", str(launch_campaign.merchant.name)).replace("@voucher_code", str(voucher_code))

                msg = EmailMessage(
                    str(subject_target),
                    str(render_to_string('please_marketing_campaign/email_templates/email_launch_merchant',
                                         {'customer': customer,
                                          'image_url': str(launch_campaign.email_image.url),
                                          'merchant_mw_offer_id': str(launch_campaign.merchant.mw_offer_id),
                                          'message_body': body_target})),
                    "Please <contact@pleaseapp.com>",
                    [str(customer.email)],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()

                print("SUCCESS: launch merchant campaign email properly sent to user " + customer.email)

            except:
                print("ERROR: failed to send launch merchant campaign email to user " + str(customer.email) + " - " + str(
                    sys.exc_info()))

            return

        customer_set = Customer.objects.filter(
            test_user=launch_campaign.test,
            neighborhood=launch_campaign.merchant.neighborhood,
            marketing=True,
            archived=False).exclude(unsubscribed_from_emails=True).order_by("?")

        print(customer_set)
        # TEST if round is ok
        customer_set_half = round(customer_set.count() / 2)
        customer_set_1 = customer_set[:customer_set_half]
        customer_set_2 = customer_set[customer_set_half:]

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(send_launch_notification, customer_set_1)

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(send_launch_email, customer_set_2)

            # Send Reporting Email
            try:

                volume = Customer.objects.filter(
                    test_user=True,
                    neighborhood=launch_campaign.merchant.neighborhood,
                    marketing=True,
                    archived=False,
                    first_name__isnull=False,
                ).count()

                volume_no_test = Customer.objects.filter(
                    neighborhood=launch_campaign.merchant.neighborhood,
                    marketing=True,
                    archived=False,
                    first_name__isnull=False,
                ).count()

                msg = EmailMessage(
                    str("Reporting Envoi Launch Campaign - " + str(launch_campaign.merchant.name)),
                    str(render_to_string(
                        'please_marketing_campaign/email_templates/email_reporting_launch_campaign.html',
                        {
                            'merchant': str(launch_campaign.merchant.name),
                            'test': launch_campaign.test,
                            'volume': volume,
                            'volume_no_test': volume_no_test,
                            'neighborhood': str(launch_campaign.merchant.neighborhood.name),
                        }
                    ),
                    ),
                    "Please <contact@pleaseapp.com>",
                    ["contact@pleaseapp.com", "nicolas.chanton@pleaseapp.com", "lea.lefebvre@engie.com"],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()

                print("SUCCESS: launch campaign reporting email properly sent")

            except:
                print("ERROR: failed to send launch campaign reporting email - " + str(sys.exc_info()))

        # Update campaign status to done
        launch_campaign.campaign_sent = True
        launch_campaign.save()

    return
