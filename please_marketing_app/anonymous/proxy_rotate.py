# -*- coding: utf-8 -*-

import requests
from django.conf import settings


def get_proxy():

    # API used : https://www.proxicity.io/api
    # Check for API rate limit

    url = "https://api.proxicity.io/v2/" + str(settings.PROXICITY_KEY) + "/proxy?protocol=http&httpsSupport=true&country=FR"

    response = requests.request("GET", url)

    ip = response.json()["ipAddress"]
    port = response.json()["port"]

    data = {'http': str('http' + "://" + str(ip) + ":" + str(port)),
            'https': str('https' + "://" + str(ip) + ":" + str(port))}

    return data
