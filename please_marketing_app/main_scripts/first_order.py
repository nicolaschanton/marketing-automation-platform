# coding: utf-8

from please_marketing_app.models import Customer, Order
import datetime
from django.conf import settings
from django.db.models import Q
import sys
from concurrent.futures import ThreadPoolExecutor
from please_marketing_script_execution.log_script import log_script


# from please_marketing_app.main_scripts.first_order import *
def flag_first_order(customer):
    target_order = Order.objects.filter(customer=customer, odoo_order_state='done').order_by("order_date").first()

    target_order.first_order = True
    target_order.save()
    return


# from please_marketing_app.main_scripts.first_order import *
def executor_flag_first_order():
    log_script(name="executor_flag_first_order", status="s")

    with ThreadPoolExecutor(max_workers=10) as executor:
        inclusion_list = list(
            Order.objects.filter(
                odoo_order_state="done",
                customer__isnull=False).distinct("customer__id").values_list("customer__id", flat=True)
        )

        exclusion_list = list(
            Order.objects.filter(
                odoo_order_state="done",
                first_order=True,
                customer__isnull=False).distinct("customer__id").values_list("customer__id", flat=True)
        )

        executor.map(flag_first_order, Customer.objects.filter(id__in=inclusion_list).exclude(id__in=exclusion_list))

    log_script(name="executor_flag_first_order", status="d")
    return
