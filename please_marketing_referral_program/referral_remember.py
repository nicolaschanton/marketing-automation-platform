# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, SmsHistory, IntercomEvent
from twilio.rest import Client
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q
import sys
from concurrent.futures import ThreadPoolExecutor
from please_marketing_script_execution.log_script import log_script
import emoji
from please_marketing_app.main_scripts.utilities import get_good_sender, has_not_received_too_many_communications


# from please_marketing_referral_program.referral_remember import *
def send_sms_remember(customer):
    if SmsHistory.objects.filter(customer=customer, send_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=10)).strftime("%s")))).count() == 0:
        if has_not_received_too_many_communications(customer=customer):
            if SmsHistory.objects.filter(customer=customer, sms_type="Campaign - Referral Code Remember").count() == 0:

                # Your Account Sid and Auth Token from twilio.com/user/account
                account_sid = str(settings.TWILIO_SID)
                auth_token = str(settings.TWILIO_TOKEN)
                client = Client(account_sid, auth_token)
                # from_phone = str(settings.TWILIO_PHONE)

                print("CURRENT CUSTOMER IS: " + customer.email + " - " + customer.phone)

                try:
                    message = client.messages.create(
                        str(customer.phone),
                        body=str(
                            str(customer.first_name)
                            + str(", parrainez vos amis : 5€ pour eux, 5€ pour vous !")
                            + str("\n")
                            + str("Votre lien : https://hello.pleaseapp.com/parrainage/parrainage?r=" + str(customer.referral_code))
                        ),
                        from_=get_good_sender(customer=customer)
                    )

                    print("SUCCESS: SMS properly sent to user ", customer.id, message.sid, message.date_created.date, message.body)

                    SmsHistory(
                        customer=customer,
                        content=message.body,
                        send_date=datetime.now(),
                        sms_type="Campaign - Referral Code Remember"
                    ).save()

                except:
                    print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def executor_send_sms_remember(neighborhoods):
    log_script(name="executor_send_sms_remember", status="s")

    with ThreadPoolExecutor(max_workers=10) as executor:

        executor.map(send_sms_remember, Customer.objects.filter(
            sign_up_date__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=15)).strftime("%s"))),
            neighborhood__in=neighborhoods,
            referral_code__isnull=False,
            total_spent__gt=0,
            marketing=True,
            archived=False,
            first_name__isnull=False,
            phone__isnull=False).order_by("?")[:100])

    log_script(name="executor_send_sms_remember", status="d")
    return


#id=8243, 6233
