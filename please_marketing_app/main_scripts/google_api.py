# coding: utf-8

from google.cloud import language_v1
from google.cloud import language
from google.cloud.language_v1 import enums
from google.cloud.language import types
import six
from django.conf import settings
import os
import googlemaps


# from please_marketing_app.main_scripts.google_api import *
# content = "Maman tire aussi bien au 38 qu'elle écrit au BIC, avant de voir Saint Nicolas j'me ferais bien un flic"
def analyze_sentiment(content):

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "please_marketing/google/PleaseMarketing-180914ffed4f.json"
    client = language_v1.LanguageServiceClient()

    if isinstance(content, six.binary_type):
        content = content.decode('utf-8')

    type_ = enums.Document.Type.PLAIN_TEXT

    document = {
        'type': type_,
        'content': content
    }

    response = client.analyze_sentiment(document)
    sentiment = response.document_sentiment
    print(response)
    print(sentiment)

    return


def geocoding(city):

    client = googlemaps.Client(key=settings.GOOGLE_API_KEY)

    geocode_result = client.geocode(str(city.replace(" ", "+")))[0]

    for dict in geocode_result.get("address_components"):
        if dict.get("types")[0] == "locality":
            city = dict.get("long_name")

    formatted_address = geocode_result.get("formatted_address")
    lat = geocode_result.get("geometry").get("location").get("lat")
    lng = geocode_result.get("geometry").get("location").get("lng")

    return formatted_address, lat, lng, city
