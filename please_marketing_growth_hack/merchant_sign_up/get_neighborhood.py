# -*- coding: utf-8 -*-
import requests
import json


# from please_marketing_growth_hack.merchant_sign_up.get_neighborhood import *
def get_neighborhood(latitude, longitude):

    url = "https://mw.please-it.com/next-mw/api/public/website/conciergerie/coordinates"

    querystring = {
        "longitude": str(longitude),
        "latitude": str(latitude),
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    return response.get("odooConciergerieId")
