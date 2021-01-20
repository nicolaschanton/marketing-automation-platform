# coding: utf-8

import requests
from please_marketing_app.models import Customer
from .models import AddressEnrichment, AddressEnrichmentSl
from django.conf import settings
import random
import json
from django.db.models import Q
import sys
from concurrent.futures import ThreadPoolExecutor
from please_marketing_app.anonymous.random_uagents import random_ua
from please_marketing_app.anonymous.proxy_rotate import get_proxy
import urllib.parse
from please_marketing_script_execution.log_script import log_script
import urllib
import time


# customer = Customer.objects.get(email="nicolas.chanton@gmail.com")
# from please_marketing_extra_user_enrichment.address_enrichment import *
def query_ma_street(customer, proxies):
    adress = str(customer.street + ", " + customer.city)

    url = "https://geo.meilleursagents.com/geo/v1/"
    querystring = {"q": adress, "types": "streets"}

    headers = {
        'authority': "api.meilleursagents.com",
        'method': "GET",
        'scheme': "https",
        'accept': "application/json, text/javascript, */*; q=0.01",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
        'origin': "https://www.meilleursagents.com",
        'user-agent': random_ua(),
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, headers=headers, params=querystring, proxies=proxies).json()

    print(response)

    slug = response.get("response").get("places")[0].get("slug")
    slug_id = response.get("response").get("places")[0].get("id")
    slug_zip = response.get("response").get("places")[0].get("zips")[0]
    slug_city = customer.city.replace(" ", "-").lower()

    return slug, slug_id, slug_zip, slug_city


def get_prices():

    for customer in Customer.objects.filter(city__isnull=False, street__isnull=False, zip__isnull=False):

        if AddressEnrichment.objects.filter(customer=customer).count() == 0:

            proxies = get_proxy()

            q = query_ma_street(customer=customer, proxies=proxies)
            slug = q[0]
            slug_id = q[1]
            slug_zip = q[2]
            slug_city = q[3]

            url = str("https://www.meilleursagents.com/prix-immobilier/" + slug_city + "-" + slug_zip + "/" + slug + "-" + slug_id + "/")  # "mantes-la-ville-78711/place-de-la-mairie-2107592/"

            querystring = {"partial": "1"}

            headers = {
                'authority': "api.meilleursagents.com",
                'method': "GET",
                'path': str("/prix-immobilier/" + slug_city + "-" + slug_zip + "/" + slug + "-" + slug_id + "/?partial=1"),
                # "/prix-immobilier/mantes-la-ville-78711/place-de-la-mairie-2107592/?partial=1"
                'scheme': "https",
                'accept': "application/json, text/javascript, */*; q=0.01",
                'accept-encoding': "gzip, deflate, br",
                'accept-language': "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
                'origin': "https://www.meilleursagents.com",
                'user-agent': random_ua(),
                # 'referer': "https://www.meilleursagents.com/prix-immobilier/mantes-la-jolie-78200/rue-des-ecoles-2101743/26/",
                'x-requested-with': "XMLHttpRequest",
                'cache-control': "no-cache",
            }

            response = requests.request("GET", url, headers=headers, params=querystring, proxies=proxies).json()

            print(response)

            rent_low_price = response.get("market").get("prices").get("rental").get("apartment").get("hybrid").get("low")
            rent_medium_price = response.get("market").get("prices").get("rental").get("apartment").get("hybrid").get(
                "value")
            rent_high_price = response.get("market").get("prices").get("rental").get("apartment").get("hybrid").get("high")

            buy_low_price = response.get("market").get("prices").get("sell").get("apartment").get("low")
            buy_medium_price = response.get("market").get("prices").get("sell").get("apartment").get("value")
            buy_high_price = response.get("market").get("prices").get("sell").get("apartment").get("high")

            AddressEnrichment(
                customer=customer,
                rent_low_price=rent_low_price,
                rent_medium_price=rent_medium_price,
                rent_high_price=rent_high_price,
                buy_low_price=buy_low_price,
                buy_medium_price=buy_medium_price,
                buy_high_price=buy_high_price,
            ).save()

            print("SUCCESS: " + str(customer.email) + " physical address has been enriched (insert)")

        elif AddressEnrichment.objects.filter(customer=customer).count() == 1:
            pass

    return


def executor_get_prices():
    log_script(name="executor_get_prices", status="s")

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(get_prices, Customer.objects.filter(city__isnull=False, street__isnull=False, zip__isnull=False))

    log_script(name="executor_get_prices", status="d")
    return


# from please_marketing_extra_user_enrichment.address_enrichment import *
def get_data_from_sl():
    log_script(name="get_data_from_sl", status="s")

    exclusion_list = list(
        AddressEnrichmentSl.objects.all(
            customer__isnull=False).distinct("customer__id").values_list("customer__id", flat=True)
    )

    for customer in Customer.objects.filter(
            city__isnull=False,
            street__isnull=False,
            zip__isnull=False).exclude(id__in=exclusion_list):

        def get_price():
            time.sleep(3)
            # First Part of the script = Get the tags
            url = "https://autocomplete.svc.groupe-seloger.com/api/v3.0/auto/complete/fr"

            headers = {
                'cache-control': "no-cache",
            }

            querystring = {
                "text": urllib.parse.quote_plus(str(customer.street + " " + customer.zip))
            }

            response = requests.request("GET", url, headers=headers, params=querystring).json()

            latitude = response.get("Addresses")[0].get("Params").get("Latitude")
            longitude = response.get("Addresses")[0].get("Params").get("Longitude")
            street = response.get("Addresses")[0].get("Params").get("Street")
            postal_code = response.get("Addresses")[0].get("Params").get("PostalCode")

            # Second Part of the script = Get the tags
            url_2 = "https://ws.lacoteimmo.com/api/LocalityV2/Get"

            payload_2 = """{\n\t\"localityType\":1,\n\t\"transactionType\":13,\n\t\"latitude\":\"""" + str(
                latitude) + """\",\n\t\"longitude\":\"""" + str(longitude) + """\",\n\t\"label\":\"""" + str(
                street) + """\",\n\t\"bu\":2,\n\t\"cp\":\"""" + str(postal_code) + """\"\n}"""

            headers_2 = {
                'Content-Type': "application/json",
                'cache-control': "no-cache",
            }

            response_2 = requests.request("POST", url_2, data=payload_2, headers=headers_2).json()

            #buy_low_price = response_2.get("summary").get("prices").get("min")
            #buy_medium_price = response_2.get("summary").get("prices").get("med")
            #buy_high_price = response_2.get("summary").get("prices").get("max")

            #print(buy_high_price, buy_medium_price, buy_low_price)

            AddressEnrichmentSl(
                customer=customer,

                # Address
                latitude=latitude,
                longitude=longitude,
                label=street,
                cp=postal_code,

                # Prices Buying Average
                summary_prices_max=response_2.get("summary").get("prices").get("max"),
                summary_prices_med=response_2.get("summary").get("prices").get("med"),
                summary_prices_min=response_2.get("summary").get("prices").get("min"),

                # House Market Data
                market_numbers_selling=response_2.get("market").get("numbers").get("selling"),
                market_numbers_sold=response_2.get("market").get("numbers").get("sold"),
                market_numbers_numberMainResidence=response_2.get("market").get("numbers").get("numberMainResidence"),
                market_numbers_numberSecondaryResidence=response_2.get("market").get("numbers").get("numberSecondaryResidence"),
                market_numbers_numberTotalResidence=response_2.get("market").get("numbers").get("numberTotalResidence"),

                # Home Composition
                single=response_2.get("neighborhood").get("homeComposition").get("single"),
                couple=response_2.get("neighborhood").get("homeComposition").get("couple"),
                family=response_2.get("neighborhood").get("homeComposition").get("family"),

                # Neighborhood Info
                poi_transport_count=response_2.get("neighborhood").get("poi").get("transport").get("count"),
                poi_education_count=response_2.get("neighborhood").get("poi").get("education").get("count"),
                poi_neighbors_count=response_2.get("neighborhood").get("poi").get("neighbors").get("count"),
                poi_hotels_count=response_2.get("neighborhood").get("poi").get("hotels").get("count"),
                poi_commerces_count=response_2.get("neighborhood").get("poi").get("commerces").get("count"),

                # Stats INSEE
                nbLogements=response_2.get("statInsee").get("nbLogements"),
                nbHabitants=response_2.get("statInsee").get("nbHabitants"),
                peopleDensity=response_2.get("statInsee").get("peopleDensity"),
                ageMed=response_2.get("statInsee").get("ageMed"),
                age25MoinsPcent=response_2.get("statInsee").get("age25MoinsPcent"),
                age25PlusPcent=response_2.get("statInsee").get("age25PlusPcent"),
                nbEntreprises=response_2.get("statInsee").get("nbEntreprises"),
                nbCreationEntreprises=response_2.get("statInsee").get("nbCreationEntreprises"),
                pcentActifsAll=response_2.get("statInsee").get("pcentActifsAll"),
                pcentActifs30=response_2.get("statInsee").get("pcentActifs30"),
                pcentUnemployed=response_2.get("statInsee").get("pcentUnemployed"),
                averageIncome=response_2.get("statInsee").get("averageIncome"),
                pcentEtudiants=response_2.get("statInsee").get("pcentEtudiants"),
                pcentResPrincipales=response_2.get("statInsee").get("pcentResPrincipales"),
                pcentResSecondaires=response_2.get("statInsee").get("pcentResSecondaires"),
                pcentLogVacants=response_2.get("statInsee").get("pcentLogVacants"),
                pcentLocataires=response_2.get("statInsee").get("pcentLocataires"),
                pcentPrpriotaires=response_2.get("statInsee").get("pcentPrpriotaires"),
                pcentAppartement=response_2.get("statInsee").get("pcentAppartement"),
                pcentMaisons=response_2.get("statInsee").get("pcentMaisons"),
            ).save()

            return

        if AddressEnrichmentSl.objects.filter(customer=customer).count() == 0:
            try:
                get_price()
            except:
                try:
                    get_price()
                except:
                    AddressEnrichmentSl(
                        customer=customer
                    ).save()
                    print("ERROR: Address not decoded - " + str(sys.exc_info()))

    log_script(name="get_data_from_sl", status="d")
    return
