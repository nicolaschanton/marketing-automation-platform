# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, IntercomEvent, NotificationHistory, Order, \
    NetPromoterScore, SmsHistory, Neighborhood
from .models import CosineSimilarityBooking, VectorBooking, VectorMerchant
from twilio.rest import Client
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count
import pytz
from django.conf import settings
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
import time
from please_marketing_app.main_scripts.utilities import strike_price
from please_marketing_app.get_vouchers.get_voucher import get_one_voucher
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from please_marketing_script_execution.log_script import log_script


# from please_marketing_recommendation.cos_sim import *
# neighborhood = Neighborhood.objects.get(mw_id=206)

def save_vector(customer, vect_customer, vect_merchant):
    if VectorBooking.objects.filter(customer=customer).count() == 0:
        VectorBooking(
            customer=customer,
            vector=vect_customer,
            vector_merchant=vect_merchant
        ).save()

    elif VectorBooking.objects.filter(customer=customer).count() == 1:
        vect_booking = VectorBooking.objects.get(customer=customer)
        vect_booking.vector = vect_customer
        vect_booking.vector_merchant = vect_merchant
        vect_booking.save()

    return


def create_vector(customer):
    vect_merchant = VectorMerchant.objects.get(neighborhood=customer.neighborhood)
    vect_customer = []

    for merchant_mw_offer_id in vect_merchant.vector:
        counter = 0 if Order.objects.filter(Q(rating__gte=3) | Q(rating=0) | Q(rating__isnull=True), odoo_order_state="done", mw_offer_id=merchant_mw_offer_id, customer=customer).count() == 0 else 1
        vect_customer.append(counter)

    save_vector(customer=customer, vect_customer=vect_customer, vect_merchant=vect_merchant)

    return


def executor_create_vector(neighborhood):
    with ThreadPoolExecutor(max_workers=20) as executor:

        merch_id_list = []
        for mw_offer_id in Order.objects.filter(neighborhood=neighborhood, mw_offer_id__isnull=False).distinct("mw_offer_id").values("mw_offer_id").order_by("mw_offer_id"):
            if Order.objects.filter(odoo_order_state="done", mw_offer_id=mw_offer_id.get("mw_offer_id")).count() > 30:
                merch_id_list.append(mw_offer_id.get("mw_offer_id"))

        if VectorMerchant.objects.filter(neighborhood=neighborhood).count() == 0:
            VectorMerchant(
                neighborhood=neighborhood,
                vector=merch_id_list,
            ).save()

        elif VectorMerchant.objects.filter(neighborhood=neighborhood).count() == 1:
            vector_merchant = VectorMerchant.objects.get(neighborhood=neighborhood)
            vector_merchant.vector = merch_id_list
            vector_merchant.save()

        cus_id_list = []
        for cus_id in Order.objects.filter(Q(rating__gte=3) | Q(rating=0) | Q(rating__isnull=True), customer__isnull=False, odoo_order_state="done", mw_offer_id__in=merch_id_list).distinct("customer").values("customer"):
            cus_id_list.append(cus_id.get("customer"))

        print(cus_id_list)
        executor.map(create_vector, Customer.objects.filter(neighborhood=neighborhood, neighborhood__isnull=False, email__isnull=False, id__in=cus_id_list))

    return


def create_all_vector_booking():
    log_script(name="create_all_vector_booking", status="s")
    for neighborhood in Neighborhood.objects.all():
        executor_create_vector(neighborhood=neighborhood)

    log_script(name="create_all_vector_booking", status="d")
    return


def cos_sim(vect_1, vect_2):
    dot_product = np.dot(np.array(vect_1), np.array(vect_2))

    norm_1 = np.linalg.norm(np.array(vect_1))
    norm_2 = np.linalg.norm(np.array(vect_2))

    return dot_product / (norm_1 * norm_2)


def cos_sim_all(customer):
    target_neighborhood = customer.neighborhood
    target_vectors = VectorBooking.objects.filter(customer__neighborhood=target_neighborhood).exclude(customer=customer)

    for target_vector in target_vectors:
        target_user = target_vector.customer

        if (CosineSimilarityBooking.objects.filter(customer_1=customer, customer_2=target_user).count() == 0) and (CosineSimilarityBooking.objects.filter(customer_1=target_user, customer_2=customer).count() == 0):

            cos_sim_value = cos_sim(vect_1=VectorBooking.objects.get(customer=customer).vector, vect_2=VectorBooking.objects.get(customer=target_user).vector)

            if (cos_sim_value > 0) and (cos_sim_value < 1):
                CosineSimilarityBooking(
                    customer_1=customer,
                    customer_2=target_user,
                    cos_sim_value=cos_sim_value,
                ).save()

        elif CosineSimilarityBooking.objects.filter(customer_1=customer, customer_2=target_user).count() == 1:
            cos_sim_booking = CosineSimilarityBooking.objects.get(customer_1=customer, customer_2=target_user)
            cos_sim_value = cos_sim(vect_1=VectorBooking.objects.get(customer=customer).vector, vect_2=VectorBooking.objects.get(customer=target_user).vector)

            if (cos_sim_value > 0) and (cos_sim_value < 1):
                cos_sim_booking.cos_sim_value = cos_sim_value
                cos_sim_booking.save()

        elif CosineSimilarityBooking.objects.filter(customer_1=target_user, customer_2=customer).count() == 1:
            cos_sim_booking = CosineSimilarityBooking.objects.get(customer_1=target_user, customer_2=customer)
            cos_sim_value = cos_sim(vect_1=VectorBooking.objects.get(customer=customer).vector, vect_2=VectorBooking.objects.get(customer=target_user).vector)

            if (cos_sim_value > 0) and (cos_sim_value < 1):
                cos_sim_booking.cos_sim_value = cos_sim_value
                cos_sim_booking.save()
    return


def executor_cos_sim_all():
    log_script(name="executor_cos_sim_all", status="s")
    with ThreadPoolExecutor(max_workers=20) as executor:
        cus_id_list = []
        for cus_id in VectorBooking.objects.all().values("customer"):
            cus_id_list.append(cus_id.get("customer"))
        executor.map(cos_sim_all, Customer.objects.filter(id__in=cus_id_list))

    log_script(name="executor_cos_sim_all", status="d")
    return
