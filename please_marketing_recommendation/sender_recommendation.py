# coding: utf-8
from django.template import loader
import copy
import json
import datetime
from django.utils import timezone
from django.http import HttpResponse
import random
from datetime import datetime
from django.conf import settings
from django.db.models import Q
import sys
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .cos_sim import get_recommendation
from please_marketing_app.models import Customer, Merchant
from please_marketing_app.get_vouchers.get_voucher import get_one_voucher


# from please_marketing_recommendation.sender_recommendation import *
def send_email_recommendation(customer):

    recommendation = get_recommendation(customer=customer, min_cos_sim_value=0.5)

    if recommendation[0] is not None:
        merchant = recommendation[0]
        code = get_one_voucher(customer=customer, notification_type='email_recommendation', voucher_name='Campagne Recommandation', voucher_validity=60, voucher_value=5, voucher_val_type='amount', first_order_only=True, first_customer_order=False, pricelist_id=merchant.odoo_offer_id, voucher_code=0)[1]

        msg = EmailMessage(
            str(customer.first_name + ", on parie que vous aimerez " + str(merchant.name)),
            str(render_to_string('please_marketing_recommendation/email_templates/email_recommendation',
                                 {
                                     'merchant': merchant,
                                     'customer': customer,
                                     'code': str(code),
                                  })),
            "Please <contact@pleaseapp.com>",
            ["nicolas.chanton@gmail.com"],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        print("SUCCESS: Recommendation Campaign Email properly sent to user " + customer.email)

    return
