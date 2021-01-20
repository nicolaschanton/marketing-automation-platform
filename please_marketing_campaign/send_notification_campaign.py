# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, Customer, Neighborhood, NotificationHistory
from please_marketing_campaign.models import NotificationCampaign
from datetime import datetime, timedelta
import sys
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
import emoji
import random
import requests
import json
import unicodedata
from please_marketing_script_execution.log_script import log_script
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .alert_slack import send_alert


# from please_marketing_campaign.send_notification_campaign import *
def send_notification_campaign():

    for notification_campaign in NotificationCampaign.objects.filter(
            campaign_sent=False,
            campaign_is_sending=False,
            campaign_send_date_time__lte=datetime.fromtimestamp(float((datetime.today()).strftime("%s")))):

        notification_campaign.campaign_is_sending = True
        notification_campaign.save()

        if notification_campaign.test is False:
            try:
                send_alert(
                    n_name=notification_campaign.campaign_name,
                    n_target_size=Customer.objects.filter(
                        neighborhood__in=notification_campaign.neighborhoods.all(),
                        marketing=True,
                        archived=False,
                        first_name__isnull=False,
                        orders_number__lte=int(notification_campaign.max_order_number),
                        orders_number__gte=int(notification_campaign.min_order_number)).count(),
                    n_nbs=[nb.name for nb in notification_campaign.neighborhoods.all()]
                )
            except:
                continue

        def send_notification(customer):

            try:
                message_variations = (str(notification_campaign.notification_content_a),
                                      str(notification_campaign.notification_content_b))

                message_target = message_variations[int(random.randint(0, len(message_variations) - 1))]

                # Update User Custom Fields
                message_target = message_target.replace("[first_name]", str(customer.first_name)).replace("[last_name]", str(customer.last_name))

                # Update Emoji Custom Fields
                pos_1 = message_target.find("[emoji.") + 7
                pos_2 = message_target.find(".emoji]")

                emoji_code = message_target[pos_1:pos_2]

                message_target = message_target.replace(message_target[(pos_1 - 7):(pos_2 + 7)], str(emoji.emojize(str(":" + str(emoji_code) + ":"), use_aliases=True)))

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

                print("SUCCESS: launch notification campaign properly sent to user " + str(customer.email))
                print(customer.first_name, customer.last_name, message_target)
                print(response.text)

                NotificationHistory(
                    customer=customer,
                    title="Notification Campaign - " + str(notification_campaign.campaign_name),
                    content=message_target,
                    abandoned_cart=False,
                    abandoned_sign_up=False,
                    rediscover=False,
                    discover=False,
                ).save()

            except:
                print("ERROR: Failed to send notification campaign for user " + str(customer.email) + " - " + str(
                    sys.exc_info()))

            return

        log_script(name=str("send_notification_campaign - " + notification_campaign.campaign_name), status="s")

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(send_notification, Customer.objects.filter(
                test_user=notification_campaign.test,
                neighborhood__in=notification_campaign.neighborhoods.all(),
                marketing=True,
                archived=False,
                first_name__isnull=False,
                orders_number__lte=int(notification_campaign.max_order_number),
                orders_number__gte=int(notification_campaign.min_order_number)
            ))

        # Update capaign status to done
        notification_campaign.campaign_sent = True
        notification_campaign.campaign_is_sending = False
        notification_campaign.save()

        # Send Reporting Email
        try:

            volume = Customer.objects.filter(
                test_user=notification_campaign.test,
                neighborhood__in=notification_campaign.neighborhoods.all(),
                marketing=True,
                archived=False,
                first_name__isnull=False,
                orders_number__lte=int(notification_campaign.max_order_number),
                orders_number__gte=int(notification_campaign.min_order_number)
            ).count()

            volume_no_test = Customer.objects.filter(
                neighborhood__in=notification_campaign.neighborhoods.all(),
                marketing=True,
                archived=False,
                first_name__isnull=False,
                orders_number__lte=int(notification_campaign.max_order_number),
                orders_number__gte=int(notification_campaign.min_order_number)
            ).count()

            msg = EmailMessage(
                str("Reporting Envoi Notification - " + str(notification_campaign.campaign_name)),
                str(render_to_string(
                    'please_marketing_campaign/email_templates/email_reporting_campaign.html',
                    {
                        'test': notification_campaign.test,
                        'volume': volume,
                        'volume_no_test': volume_no_test,
                        'var_a': str(notification_campaign.notification_content_a),
                        'var_b': str(notification_campaign.notification_content_b),
                        'neighborhoods': [nb.name for nb in notification_campaign.neighborhoods.all()],
                        'max_order_number': notification_campaign.max_order_number,
                        'min_order_number': notification_campaign.min_order_number,
                    }
                ),
                ),
                "Please <contact@pleaseapp.com>",
                ["contact@pleaseapp.com", "nicolas.chanton@pleaseapp.com", "lea.lefebvre@engie.com"],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            print("SUCCESS: notification campaign reporting email properly sent")

        except:
            print("ERROR: failed to send notification campaign reporting email - " + str(sys.exc_info()))

        log_script(name=str("send_notification_campaign - " + notification_campaign.campaign_name), status="d")

    return
