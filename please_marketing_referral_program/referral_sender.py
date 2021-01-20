# coding: utf-8

from django.template import loader
import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import ReferralLead, ReferralMatch
from .forms import SendEmailReferralForm, SendSmsReferralForm
import random
from twilio.rest import Client
from datetime import datetime
from django.conf import settings
from django.db.models import Q
import sys
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from please_marketing_app.main_scripts.utilities import get_good_sender


# from please_marketing_referral_program.referral_sender import *
def send_email_referral(email, referrer, latest_booking):
    if ReferralLead.objects.filter(lead_email=email).count() < 2:
        msg = EmailMessage(
            str(referrer.first_name + " " + referrer.last_name + " vous offre un repas aujourd'hui !"),
            str(render_to_string('please_marketing_referral_program/email_templates/email_parrainage',
                                 {'referrer': referrer, 'latest_booking': latest_booking})),
            "Please <contact@pleaseapp.com>",
            [email],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        print("SUCCESS: Referral Campaign Email properly sent from user " + referrer.email + " to " + email)

        ReferralLead(
            referrer=referrer,
            lead_email=email
        ).save()

        referrer.referral_leads_counter = (0 if not referrer.referral_leads_counter else referrer.referral_leads_counter) + 1
        referrer.save()

    else:
        pass

    return


def send_email_reward(referrer, referee, voucher_code):
    msg = EmailMessage(
        str(referrer.first_name + ", 5€ offerts grâce à votre filleul Please !"),
        str(render_to_string('please_marketing_referral_program/email_templates/email_reward',
                             {'referrer': referrer, 'referee': referee, 'voucher_code': voucher_code})),
        "Please <contact@pleaseapp.com>",
        [str(referrer.email)],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    print("SUCCESS: Referral Reward Email properly sent to user " + referrer.email)

    return


def send_sms_referral(formatted_phone, referrer):
    if ReferralLead.objects.filter(lead_sms=formatted_phone).count() < 2:
        # Your Account Sid and Auth Token from twilio.com/user/account
        account_sid = str(settings.TWILIO_SID)
        auth_token = str(settings.TWILIO_TOKEN)
        client = Client(account_sid, auth_token)
        # from_phone = str(settings.TWILIO_PHONE)

        try:
            message = client.messages.create(
                to=str(formatted_phone),
                body=str(
                    "Bonjour ! "
                    + str(referrer.first_name)
                    + " vous offre 5€ avec le code "
                    + str(referrer.referral_code)
                    + " pour venir découvrir Please et vous faire livrer vos restaurants préférés !"
                    + "\n"
                    + "http://onelink.to/pleaseapp !"
                ),
                from_=get_good_sender(customer=referrer)
            )

            print("SUCCESS: Referral Campaign SMS properly sent from user ", referrer.email, message.sid,
                  message.date_created.date,
                  message.body)

            ReferralLead(
                referrer=referrer,
                lead_sms=formatted_phone.replace(" ", "")
            ).save()

            referrer.referral_leads_counter = (0 if not referrer.referral_leads_counter else referrer.referral_leads_counter) + 1
            referrer.save()

        except:
            print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    else:
        pass

    return
