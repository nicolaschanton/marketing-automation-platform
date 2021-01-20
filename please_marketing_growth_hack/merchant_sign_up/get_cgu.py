# -*- coding: utf-8 -*-
import requests
import json


# from please_marketing_growth_hack.merchant_sign_up.get_cgu import *
def get_cgu():
    url = "https://mw.please-it.com/next-mw/api/public/cgu/valid"

    querystring = {
        "type": "CGUH",
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    return response
