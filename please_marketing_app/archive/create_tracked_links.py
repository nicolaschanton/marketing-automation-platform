# -*- coding: utf-8 -*-

from please_marketing_app.models import PleaseItem, Merchant
from please_marketing_facebook.models import FacebookCatalog
import requests
import datetime
from pytz import timezone
import sys
from django.conf import settings
import csv


# https://www.pleaseapp.com/?utm_source=Google%20Business&utm_medium=Commercants%20Houilles&utm_campaign=Commercants%20Partenaires#/offers/2956
def create_google_business_links():
    with open("/Users/nicolaschanton/Desktop/links_google_business.csv", "wt") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        filewriter.writerow(
            [
                "Nom Commerce",
                "Quartier",
                "Lien",
            ]
        )

        for merchant in Merchant.objects.filter(

            name__isnull=False,
            neighborhood__isnull=False,
            mw_offer_id__isnull=False,
                ).exclude(mw_offer_id=""):

            try:

                filewriter.writerow(
                    [
                        str(merchant.name),
                        str(merchant.neighborhood.name.replace(" ", "")),
                        str("https://www.pleaseapp.com/?utm_source=Google%20Business&utm_medium=Commercants%20"
                            + str(merchant.neighborhood.name.replace(" ", ""))
                            + "&utm_campaign=Commercants%20Partenaires#/offers/"
                            + str(merchant.mw_offer_id)
                            )
                    ]
                )
                print("SUCCESS")

            except:
                print("ERROR")

    return


def create_facebook_business_links():
    with open("/Users/nicolaschanton/Desktop/links_facebook_business.csv", "wt") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        filewriter.writerow(
            [
                "Nom Commerce",
                "Quartier",
                "Lien",
            ]
        )

        for merchant in Merchant.objects.filter(

            name__isnull=False,
            neighborhood__isnull=False,
            mw_offer_id__isnull=False,
                ).exclude(mw_offer_id=""):

            try:

                filewriter.writerow(
                    [
                        str(merchant.name),
                        str(merchant.neighborhood.name.replace(" ", "")),
                        str("https://www.pleaseapp.com/?utm_source=Facebook%20Business&utm_medium=Commercants%20"
                            + str(merchant.neighborhood.name.replace(" ", ""))
                            + "&utm_campaign=Commercants%20Partenaires#/offers/"
                            + str(merchant.mw_offer_id)
                            )
                    ]
                )
                print("SUCCESS")

            except:
                print("ERROR")

    return
