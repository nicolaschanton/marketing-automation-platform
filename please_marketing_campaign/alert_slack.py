# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, Customer, Neighborhood, NotificationHistory
from please_marketing_campaign.models import NotificationCampaign
from datetime import datetime, timedelta
import pytz
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


# from please_marketing_campaign.alert_slack import *
def send_alert(n_name, n_target_size, n_nbs):

    europe_time = pytz.timezone('Europe/Paris')
    img_url = "https://www.pinclipart.com/picdir/big/98-987823_computer-icons-exclamation-mark-asterisk-image-file-nida.png"

    def get_colour(number):

        all_users = Customer.objects.all().count()
        ratio = number / all_users
        print(ratio)

        if ratio >= 0.6:
            hex_colour = "#FF0000"

        elif ratio >= 0.3:
            hex_colour = "#FFFF00"

        else:
            hex_colour = "#00FF00"

        return hex_colour

    try:
        url = "https://hooks.slack.com/services/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"

        payload = {
          "channel": "please-campaign",
          "attachments": [
                {
                    "fallback": "Campaign Info:",
                    "color": get_colour(number=n_target_size),
                    "fields": [
                        {
                            "title": "Campaign Info:",
                            "value": "Name:  " + str(n_name) + " "
                                     "\n Users:  " + str(n_target_size) + " "
                                     "\n Neighborhoods:  " + str(', '.join(n_nbs)) + " ",
                            "short": False
                        }
                    ],
                    "footer": " Date/Time: " + str(datetime.now(europe_time).strftime("%a %b %y %H:%M:%S CET %Y")) + " ",
                    "footer_icon": img_url,

                }
            ]
        }

        headers = {
            'Content-Type': "application/json",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "hooks.slack.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        print(response.text)

        print("SUCCESS: Slack Alert Properly Sent")

    except:
        print("ERROR: Failed To Send Slack Alert - " + str(sys.exc_info()))

    return
