# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, Customer, Neighborhood, SmsHistory
from please_marketing_campaign.models import SmsCampaign
from twilio.rest import Client
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
from please_marketing_app.main_scripts.utilities import get_good_sender


# from please_marketing_campaign.send_sms_campaign import *
def send_sms_campaign():

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    for sms_campaign in SmsCampaign.objects.filter(
            campaign_sent=False,
            campaign_is_sending=False,
            campaign_send_date_time__lte=datetime.fromtimestamp(float((datetime.today()).strftime("%s")))):

        sms_campaign.campaign_is_sending = True
        sms_campaign.save()

        def send_sms(customer):
            try:
                message_variations = (str(sms_campaign.sms_content_a),
                                      str(sms_campaign.sms_content_b))

                message_target = message_variations[int(random.randint(0, len(message_variations) - 1))]

                # Update User Custom Fields
                message_target = message_target.replace("[first_name]", str(customer.first_name)).replace("[last_name]", str(customer.last_name))

                # Update Emoji Custom Fields
                if message_target.find("[emoji.") == -1:
                    pass
                else:
                    pos_1 = message_target.find("[emoji.") + 7
                    pos_2 = message_target.find(".emoji]")

                    emoji_code = message_target[pos_1:pos_2]

                    message_target = message_target.replace(message_target[(pos_1 - 7):(pos_2 + 7)], str(emoji.emojize(str(":" + str(emoji_code) + ":"), use_aliases=True)))

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
                    sms_type=str("Campaign - " + str(sms_campaign.campaign_name))
                ).save()

            except:
                print("ERROR: Failed to send SMS campaign for user " + str(customer.email) + " - " + str(
                    sys.exc_info()))

            return

        log_script(name=str("send_sms_campaign - " + sms_campaign.campaign_name), status="s")

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(send_sms, Customer.objects.filter(
                test_user=sms_campaign.test,
                neighborhood__in=sms_campaign.neighborhoods.all(),
                marketing=True,
                archived=False,
                first_name__isnull=False,
                orders_number__lte=int(sms_campaign.max_order_number),
                orders_number__gte=int(sms_campaign.min_order_number)
            ))

        # Update capaign status to done
        sms_campaign.campaign_sent = True
        sms_campaign.campaign_is_sending = False
        sms_campaign.save()

        # Send Reporting Email
        try:

            volume = Customer.objects.filter(
                test_user=sms_campaign.test,
                neighborhood__in=sms_campaign.neighborhoods.all(),
                marketing=True,
                archived=False,
                first_name__isnull=False,
                orders_number__lte=int(sms_campaign.max_order_number),
                orders_number__gte=int(sms_campaign.min_order_number)
            ).count()

            volume_no_test = Customer.objects.filter(
                neighborhood__in=sms_campaign.neighborhoods.all(),
                marketing=True,
                archived=False,
                first_name__isnull=False,
                orders_number__lte=int(sms_campaign.max_order_number),
                orders_number__gte=int(sms_campaign.min_order_number)
            ).count()

            msg = EmailMessage(
                str("Reporting Envoi Campagne SMS - " + str(sms_campaign.campaign_name)),
                str(render_to_string(
                    'please_marketing_campaign/email_templates/email_reporting_campaign.html',
                    {
                        'test': sms_campaign.test,
                        'volume': volume,
                        'volume_no_test': volume_no_test,
                        'var_a': str(sms_campaign.sms_content_a),
                        'var_b': str(sms_campaign.sms_content_b),
                        'neighborhoods': [nb.name for nb in sms_campaign.neighborhoods.all()],
                        'max_order_number': sms_campaign.max_order_number,
                        'min_order_number': sms_campaign.min_order_number,
                    }
                ),
                ),
                "Please <contact@pleaseapp.com>",
                ["contact@pleaseapp.com", "nicolas.chanton@pleaseapp.com", "lea.lefebvre@engie.com"],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            print("SUCCESS: sms campaign reporting email properly sent")

        except:
            print("ERROR: failed to send sms campaign reporting email - " + str(sys.exc_info()))

        log_script(name=str("send_sms_campaign - " + sms_campaign.campaign_name), status="d")

    return
