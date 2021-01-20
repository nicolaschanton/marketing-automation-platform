# -*- coding: utf-8 -*-

from please_marketing_app.models import Merchant, CityManager, Customer
from please_marketing_app.get_vouchers.get_voucher import get_one_voucher
from please_marketing_merchant_campaign.models import MerchantTestLaunchCampaign
import datetime
from twilio.rest import Client
import sys
from django.conf import settings


def send_test_launch_campaign():
    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    merchants_id_to_exclude = []

    for campaign in MerchantTestLaunchCampaign.objects.filter(campaign_sent=True):
        merchants_id_to_exclude.append(campaign.merchant.id)

    for merchant in Merchant.objects.filter(launch_date=datetime.date.today()).exclude(id__in=merchants_id_to_exclude):
        city_manager = CityManager.objects.get(neighborhoo=merchant.neighborhood)
        customer = city_manager.customer
        voucher_code = get_one_voucher(
            customer=customer,
            notification_type="Test Offre Partenaire SMS",
            voucher_validity=2,
            voucher_value=20,
            voucher_val_type='amount',
            voucher_code=0,
            first_customer_order=False,
            first_order_only=True,
            voucher_name=str("Test Offre " + merchant.name + " - 20€"),
            pricelist_id=merchant.odoo_offer_id)[1]

        try:
            message = client.messages.create(
                str("+33" + customer.phone.lstrip("0")),
                body=str(
                    customer.first_name + ", voici un coupon de 20€ pour tester l'offre " + merchant.name + ". Code : " + voucher_code + ". Attention code valide seulement 24h !\nL'équipe Please"),
                from_=from_phone
            )

            print("SUCCESS: SMS properly sent to city_manager ", customer.id, message.sid, message.date_created.date, message.body)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.datetime.now(),
                sms_type="Campaign - Launch Merchant City Manager's Test"
            ).save()

            MerchantTestLaunchCampaign(
                merchant=merchant,
                campaign_sent=True
            ).save()

        except:
            print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return
