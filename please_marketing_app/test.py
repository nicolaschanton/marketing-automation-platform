# coding: utf-8
from please_marketing_app.models import Customer, Order
from twilio.rest import Client
from django.conf import settings
from datetime import datetime, timedelta
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor
from django.db.models import Count, Avg, Sum, FloatField


# from please_marketing_app.test import *
def executor_time_between_1_2_orders():
    list_of_delays = []

    def time_between_1_2_orders(cus):
        target_orders = Order.objects.filter(
            customer=cus,
            odoo_order_state="done",
        ).order_by("order_date")

        if target_orders.count() >= 2:
            target_orders = target_orders[:2]

            date1 = target_orders[0].order_date
            date2 = target_orders[1].order_date

            delay = int((date2 - date1).days)
            if delay < 200:
                list_of_delays.append(delay)

        return

    with ThreadPoolExecutor(max_workers=50) as executor:
        target_customers = Customer.objects.filter(
            orders_number__gte=2
        ).order_by("?")[:10000]

        executor.map(
            time_between_1_2_orders,
            target_customers
        )

        return list_of_delays


# from please_marketing_app.test import *
def calculate():

    list_of_delays = executor_time_between_1_2_orders()

    # List
    list_of_delays.sort()
    print(list_of_delays)

    # Creating the Series
    sr = pd.Series(list_of_delays)
    print(sr.std())

    avg_list = sum(list_of_delays) / len(list_of_delays)

    print(avg_list)

    g = sns.distplot(list_of_delays)
    plt.show()
    return


# from please_marketing_app.test import *
def cus_seg_1():
    customer_data = pd.DataFrame.from_records(
        Customer.objects.filter(orders_number__gte=2)
            .annotate(average_voucher=Sum("total_voucher", output_field=FloatField()) / Sum("orders_number", output_field=FloatField()))
            .values(
            "average_basket",
            "average_voucher",
            "neighborhood__name"
        )
    )

    filtered_data = customer_data[
        (customer_data['average_basket'] < 80)
        & (customer_data['average_voucher'] < 20)
        & (customer_data['neighborhood__name'] != "PAU")
        & (customer_data['neighborhood__name'] != "HOUILLES")
        & (customer_data['neighborhood__name'] != "LE PERREUX-SUR-MARNE")
        ]

    sns.violinplot(x="neighborhood__name", y="average_basket", data=filtered_data, palette="muted")
    plt.show()

    return


# from please_marketing_app.test import *
def cus_seg_2():
    customer_data = pd.DataFrame.from_records(
        Customer.objects.filter(orders_number__gte=2)
            .annotate(average_voucher=Sum("total_voucher", output_field=FloatField()) / Sum("orders_number", output_field=FloatField()))
            .values(
            "average_basket",
            "average_voucher"
        )
    )

    filtered_data = customer_data[
        (customer_data['average_basket'] < 80)
        & (customer_data['average_voucher'] < 20)
        ]

    sns.set(style="whitegrid")
    sns.scatterplot(
        x="average_basket",
        y="average_voucher",
        palette="ch:r=-.2,d=.3_r",
        linewidth=0,
        data=filtered_data,
        color="b"
    )

    plt.show()

    return


# from please_marketing_app.test import *
def cus_seg_3():
    customer_data = pd.DataFrame.from_records(
        Customer.objects.filter(orders_number__gte=2)
            .annotate(average_voucher=Sum("total_voucher", output_field=FloatField()) / Sum("orders_number", output_field=FloatField()))
            .values(
            "average_basket",
            "average_voucher"
        )
    )

    print("#### STARS #####")
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__lte=5).count())
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__lte=5).aggregate(
        Avg('average_basket')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__lte=5).aggregate(
        Sum('total_spent')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__lte=5).aggregate(
        Sum('total_voucher')))


    print("#### CASH COWS #####")
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__lte=5).count())
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__lte=5).aggregate(
        Avg('average_basket')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__lte=5).aggregate(
        Sum('total_spent')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__lte=5).aggregate(
        Sum('total_voucher')))

    print("#### QUESTION MARKS #####")
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__gt=5).count())
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__gt=5).aggregate(
        Avg('average_basket')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__gt=5).aggregate(
        Sum('total_spent')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__gte=30, total_voucher__gt=5).aggregate(
        Sum('total_voucher')))

    print("#### LEMONS #####")
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__gt=5).count())
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__gt=5).aggregate(
        Avg('average_basket')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__gt=5).aggregate(
        Sum('total_spent')))
    print(Customer.objects.filter(orders_number__gte=2, average_basket__lt=30, total_voucher__gt=5).aggregate(
        Sum('total_voucher')))



    #filtered_data = customer_data[
    #    (customer_data['average_basket'] > 30)
    #    & (customer_data['average_voucher'] < 5)
    #    ]
#
    #sns.jointplot(
    #    "average_basket",
    #    "average_voucher",
    #    data=filtered_data,
    #    kind="reg",
    #    xlim=(30, 80),
    #    ylim=(0, 5),
    #    color="m",
    #    height=7
    #)
#
    #plt.show()

    return
