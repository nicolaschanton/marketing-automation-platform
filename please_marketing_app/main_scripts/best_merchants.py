# coding: utf-8

import requests
import json
import sys
from bs4 import BeautifulSoup
from please_marketing_app.models import Order, Merchant, Neighborhood
from datetime import datetime, timedelta
from please_marketing_script_execution.log_script import log_script


# from please_marketing_app.main_scripts.best_merchants import *
def elect_best_merchants():
    log_script(name="elect_best_merchants", status="s")
    for neighborhood in Neighborhood.objects.all().exclude(mw_id=105):
        merchant_rank_list = []
        for merchant in Order.objects.filter(neighborhood=neighborhood, odoo_order_state='done', mw_offer_id__isnull=False, order_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(days=1200)).strftime("%s")))).distinct("mw_offer_id").values("mw_offer_id"):
            counter = Order.objects.filter(neighborhood=neighborhood, odoo_order_state='done', mw_offer_id=merchant.get("mw_offer_id"), order_date__gte=datetime.fromtimestamp(float((datetime.today() - timedelta(days=1200)).strftime("%s")))).count()
            merchant_rank_list.append((merchant.get("mw_offer_id"), counter))

        Merchant.objects.filter(neighborhood=neighborhood).update(five_best=False)
        best_merchants = sorted(merchant_rank_list, key=lambda order: order[1], reverse=True)[:5]

        for merchant_mw_offer_id in best_merchants:
            try:
                merchant = Merchant.objects.get(mw_offer_id=merchant_mw_offer_id[0])
                merchant.five_best = True
                merchant.save()
            except:
                print("ERROR: not updating best merchant for merchant - " + str(merchant_mw_offer_id[0]))
    log_script(name="elect_best_merchants", status="d")
    return
