# -*- coding: utf-8 -*-
from please_marketing_app.models import Merchant
import requests
import datetime
from pytz import timezone
import sys
from django.conf import settings
import json
from concurrent.futures import ThreadPoolExecutor
from please_marketing_app.anonymous.proxy_rotate import get_proxy
from please_marketing_app.anonymous.random_uagents import random_ua


# from please_marketing_app.local_scripts.load_tests_please import *
def test_viewed_offer(mw_offer_id):

    try:
        url = str("https://mw-dev.please-it.com/next-mw-website/api/public/website/services/menu/" + str(mw_offer_id))

        headers = {
            'Cache-Control': "no-cache",
            'user-agent': random_ua(),
        }

        response = requests.request("GET", url, headers=headers).json()

        print(response)

    except:
        print(str("ERROR: " + str(sys.exc_info())))


def executor_test_viewed_offer(multiple):
    mw_offer_ids = []
    for mw_offer in Merchant.objects.filter(mw_offer_id__isnull=False):
        mw_offer_ids.append(mw_offer.mw_offer_id)

    shit = mw_offer_ids
    while multiple > 0:
        shit += mw_offer_ids
        multiple -= 1

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(test_viewed_offer, shit)
    return


def test_viewed_universe(rang):
    print(rang)

    try:
        url_dev = "https://mw-dev.please-it.com/next-mw/api/public/website/categories/withConnections?lat=48.9922608&lon=1.7112108999999691"
        url_preprod = "https://mw-preprod.please-it.com/next-mw/api/public/website/categories/withConnections?lat=48.9922608&lon=1.7112108999999691"
        url_prod = ""

        headers = {
            'Cache-Control': "no-cache",
        }

        requests.request("GET", url_dev, headers=headers).json()

    except:
        print(str("ERROR: " + str(sys.exc_info())))


def executor_test_viewed_universe():
    rang = []

    i = 0
    while i < 10000:
        rang.append(i)
        i = i + 1
    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(test_viewed_universe, rang)
    return


def test_viewed_neighborhood():

    try:
        url_dev = "https://mw-dev.please-it.com/next-mw/api/public/website/categories/withConnections?lat=48.9922608&lon=1.7112108999999691"
        url_preprod = "https://mw-preprod.please-it.com/next-mw/api/public/website/categories/withConnections?lat=48.9922608&lon=1.7112108999999691"
        url_prod = "https://mw.please-it.com/next-mw/api/public/website/images?lon=1.7112108999999691&lat=48.9922608"

        headers = {
            'Cache-Control': "no-cache",
            'user-agent': random_ua(),
        }

        print(requests.request("GET", url_preprod, headers=headers).json())

    except:
        print(str("ERROR: " + str(sys.exc_info())))


# from please_marketing_app.local_scripts.load_tests_please import *
def executor_test_viewed_neighborhood(multiple):
    rang = [1] * multiple
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(test_viewed_neighborhood, rang)
    return
