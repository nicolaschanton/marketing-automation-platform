# -*- coding: utf-8 -*-
import requests
import json


# from please_marketing_growth_hack.merchant_sign_up.verif_phone import *
def verif_phone(phone):

    url = "https://mw.please-it.com/next-mw/api/public/user/mobileNumber/exists"

    querystring = {
        "mobileNumber": str(phone),  # "0622695505"
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    return response
