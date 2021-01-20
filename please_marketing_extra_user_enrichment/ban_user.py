# coding: utf-8

import requests
from please_marketing_app.models import Customer, Order
from django.conf import settings
import random
import json
from django.db.models import Q
import sys
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
from please_marketing_script_execution.log_script import log_script


# customer = Customer.objects.get(email="nicolas.chanton@gmail.com")
# from please_marketing_extra_user_enrichment.ban_user import *
def ban_user(customer):
    # Ban Based on Fast-Food Cheap Cuts
    if (Order.objects.filter(
            customer=customer,
            odoo_order_state='done',
            universe_name="Fast Food",
            click_and_collect=True).count() > 0) \
            or \
            (Order.objects.filter(
                customer=customer,
                odoo_order_state='done',
                universe_name="Fast Food",
                paid_amount__lt=10).count() > 0) \
            or (Customer.objects.filter(phone=customer.phone, baned=True).exclude(id=customer.id).count() > 0):

        customer.baned = True
        customer.save()

    return


def executor_ban_user():
    log_script(name="executor_ban_user", status="s")

    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(ban_user, Customer.objects.filter(baned__isnull=True))

    log_script(name="executor_ban_user", status="d")
    return
