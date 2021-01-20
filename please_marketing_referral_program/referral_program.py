# coding: utf-8

from please_marketing_app.models import Customer, Merchant, IntercomEvent, NotificationHistory, Order, NetPromoterScore, SmsHistory
from .models import ReferralMatch, ReferralLead
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
from please_marketing_app.get_vouchers.get_voucher_referral import get_one_voucher_referral
from please_marketing_app.get_vouchers.get_voucher_referral_reward import get_one_voucher_reward
from .referral_sender import send_email_reward
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from please_marketing_script_execution.log_script import log_script
from please_marketing_app.main_scripts.utilities import get_good_sender


# CREATE REFERRAL CODES FOR EVERY USER
def create_referral_code():
    log_script(name="create_referral_code", status="s")

    for customer in Customer.objects.filter(referral_code__isnull=True, odoo_user_id__isnull=False, first_name__isnull=False, last_name__isnull=False):  # Order.objects.filter(Q(rating__gte=3) | Q(rating=0) | Q(rating__isnull=True), odoo_order_state='done', customer__isnull=False, customer__referral_code__isnull=True).values('customer').distinct():

        try:

            if customer.referral_code is None:
                print("Ongoing ReferralCode creation for user " + customer.email)

                res_voucher = get_one_voucher_referral(
                    customer=customer,
                    voucher_name=str("Coupon Parrain " + customer.first_name + " " + customer.last_name),
                    voucher_code=str(unicodedata.normalize('NFD', str(customer.first_name[:9].upper() + customer.last_name[:4].upper() + str(random.randint(10, 99))).replace(" ", "").replace("-", "").replace("'", "")).encode('ascii', 'ignore').decode('UTF-8')),
                    voucher_value=5,
                    voucher_val_type='amount',
                    voucher_validity=730,
                    minimum_cart_amount=20,
                )

                voucher_code = res_voucher
                customer.referral_code = voucher_code
                customer.save()

                print("SUCCESS: referral code generated for user " + str(customer.email) + " - " + voucher_code)

            else:
                print("ERROR: referral code already generated for user " + str(customer.email) + " - " + customer.referral_code)

        except:
            print("ERROR: - " + str(sys.exc_info()))

    log_script(name="create_referral_code", status="d")
    return


# SEND VOUCHER CODE THROUGH SMS TO EVERY USER WHO HAS A REFERRALMATCH SMS SENT FALSE
def send_referral_reward(referrer, referee):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    # from_phone = str(settings.TWILIO_PHONE)

    try:
        res_voucher = get_one_voucher_reward(
            customer=referrer,
            voucher_name=str("Coupon Reward Parrainage pour " + referrer.email),
            notification_type="SMS Coupon Reward Parrainage",
            voucher_code=0,
            first_customer_order=False,
            first_order_only=False,
            voucher_value=5,
            voucher_val_type='amount',
            pricelist_id=False,
            voucher_validity=30,
            minimum_cart_amount=20,
            total_available=1,
        )

        voucher_code = res_voucher[1]

        message = client.messages.create(
            str(referrer.phone),
            body=str(
                "Bonjour "
                + str(referrer.first_name)
                + ", grâce à "
                + str(referee.first_name)
                + " vous venez de gagner 5€ dans Please avec le code "
                + str(voucher_code)
                + " "
                + emoji.emojize(u':gift:', use_aliases=True)
                + "!"
            ),
            from_=get_good_sender(customer=referrer)
        )

        print(message.sid, message.date_created.date, message.body)

        SmsHistory(
            customer=referrer,
            content=message.body,
            send_date=datetime.now(),
            sms_type="send_referral_reward",
        ).save()

        referral_match = ReferralMatch.objects.get(referee=referee, referrer=referrer)
        referral_match.sms = SmsHistory.objects.filter(customer=referrer, sms_type="send_referral_reward", send_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(seconds=5)).strftime("%s")))).first()
        referral_match.save()

        referrer.referral_counter = ReferralMatch.objects.filter(referrer=referrer).count()
        referrer.save()

        send_email_reward(referrer=referrer, referee=referee, voucher_code=voucher_code)

        print("SUCCES: SMS properly sent for send_referral_reward SMS to user " + referrer.email + " - " + referrer.phone)

    except (KeyError, AttributeError):
        print("ERROR: Twilio API Error - Message for send_referral_reward SMS not sent")

    return


# RETRIEVE ANY REFERRAL CODE USED BY SOMEONE AND SAVE IT TO DB
def retrieve_used_referral_codes(referee):
    print("CURRENT USER WORKING ON FOR REFERRAL MATCH: " + str(referee.email))
    for order in Order.objects.filter(customer=referee, odoo_order_state='done', voucher_code__isnull=False):
        referrer = Customer.objects.get(referral_code=order.voucher_code)

        # Check if there is no auto referral
        if referee != referrer:

            # Check if there's a matching referral code
            if Customer.objects.filter(referral_code=order.voucher_code).count() == 1:

                # Check if referee's phone number is unique
                if Customer.objects.filter(phone=referee.phone).count() == 1:

                    # Check if referrer's phone number is unique
                    if Customer.objects.filter(phone=referrer.phone).count() == 1:

                        # Check if referral match has not been previously created
                        if ReferralMatch.objects.filter(referee=referee, referrer=referrer).count() == 0:
                            # Create ReferralMatch
                            ReferralMatch(
                                referrer=referrer,
                                referee=referee,
                            ).save()

                            print("SUCCESS: Referral Match properly created for Referrer "
                                  + str(referrer.email)
                                  + " and Referee "
                                  + str(referee.email))

                            send_referral_reward(referrer=referrer, referee=referee)

                        elif ReferralMatch.objects.filter(referee=referee, referrer=referrer).count() == 1:
                            print("SUCCESS: Referral Match already created for Referrer "
                                  + str(referrer.email)
                                  + " and Referee "
                                  + str(referee.email))
    return


# from please_marketing_referral_program.referral_program import *
def executor_retrieve_used_referral_codes():
    log_script(name="executor_retrieve_used_referral_codes", status="s")
    with ThreadPoolExecutor(max_workers=10) as executor:
        customer_ids = []

        for customer_id in Order.objects.filter(
                odoo_order_state='done',
                customer__isnull=False,
                voucher_code__isnull=False,
                order_date__gte=datetime.fromtimestamp(
                    float((datetime.today() - timedelta(days=5)).strftime("%s")))).values('customer').distinct():
            customer_ids.append(customer_id.get("customer"))

        executor.map(retrieve_used_referral_codes, Customer.objects.filter(id__in=customer_ids))
    log_script(name="executor_retrieve_used_referral_codes", status="d")
    return


def update_intercom_user(email, first_name, last_name, phone, neighborhood, street, city, zip, longitude, latitude,
                             marketing, sign_up_date, from_referral_lead):
        try:
            url = "https://api.intercom.io/users"

            custom_attributes = {
                "signed_up": False if sign_up_date == "" else True,
                "first_name": first_name,
                "last_name": last_name,
                "street": street,
                "zip": zip,
                "city": city,
                "w_longitude": longitude,
                "w_latitude": latitude,
                "neighborhood": neighborhood.name,
                "neighborhood_odoo_id": neighborhood.odoo_id,
                "neighborhood_mw_id": neighborhood.mw_id,
                "marketing": marketing,
                "archived": False,
                "from_referral_lead": from_referral_lead
            }

            payload = {
                "user_id": email,
                "email": email,
                "phone": phone,
                "name": str(str(first_name) + " " + str(last_name)),
                "signed_up_at": sign_up_date,  # sign_up_date.strftime("%s")
                "custom_attributes": custom_attributes,
            }

            headers = {
                'accept': "application/json",
                'content-type': "application/json",
                'authorization': str(settings.INTERCOM_KEY),
                'cache-control': "no-cache"
            }

            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

            if response.json().get("type") == "error.list":
                print("ERROR: " + str(email) + " - error.list from Intercom - " + response.json().get("type"))
                status = "NOK"
                return status

            elif response.json().get("type") == "user":
                print("SUCCESS: " + str(email) + " has been created in Intercom DB from referral program leads")
                status = "OK"
                return status

            else:
                print("ERROR: " + str(
                    email) + " hasn't been created in Intercom DB from referral program leads - unexpected error")
                status = "NOK"
                return status

        except:
            print(str("ERROR: " + str(email) + " hasn't been created in Intercom DB from referral program leads - " + str(
                sys.exc_info())))
            status = "NOK"
            return status


# Send Email Leads to Intercom
def send_leads_to_intercom():
    for lead in ReferralLead.objects.filter(lead_email__isnull=False, sent_to_intercom=False)[:50]:
        response = update_intercom_user(
            email=lead.lead_email,
            first_name="",
            last_name="",
            phone="",
            neighborhood=lead.referrer.neighborhood,
            street="",
            city="",
            zip="",
            longitude="",
            latitude="",
            marketing=False,
            sign_up_date="",
            from_referral_lead=True
        )
        if response == "OK":
            lead.sent_to_intercom = True
            lead.save()
    return
