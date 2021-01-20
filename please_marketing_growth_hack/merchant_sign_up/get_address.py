# -*- coding: utf-8 -*-
import requests
import json
from django.conf import settings


# from please_marketing_growth_hack.merchant_sign_up.get_address import *
# get_address(street='1 place de la mairie', city='Mantes', zip='78200')
def get_address(address):

    customer_query = str(address)

    url = "https://maps.googleapis.com/maps/api/geocode/json"

    querystring = {
        "address": str(customer_query.replace(" ", "+")),  # "1600+Amphitheatre+Parkway,+Mountain+View,+CA",
        "key": str(settings.GOOGLE_GEOCODING_KEY)
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    if response.get("status") == "OK":

        latitude = response.get("results")[0].get("geometry").get("location").get("lat")
        longitude = response.get("results")[0].get("geometry").get("location").get("lng")

        street_number = response.get("results")[0].get("address_components")[0].get("long_name")
        route = response.get("results")[0].get("address_components")[1].get("long_name")
        locality = response.get("results")[0].get("address_components")[2].get("long_name")
        postal_code = response.get("results")[0].get("address_components")[6].get("long_name")

        street = str(street_number) + " " + str(route)
        city = str(locality)
        zip = str(postal_code)

        return latitude, longitude, street, city, zip
