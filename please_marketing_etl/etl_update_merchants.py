# -*- coding: utf-8 -*-

from please_marketing_script_execution.log_script import log_script
from please_marketing_app.models import Order, Customer, Merchant, Neighborhood
from django.conf import settings
import psycopg2.extensions
import psycopg2
import json
import sys
import requests
from django.core.mail import EmailMessage


# from please_marketing_etl.etl_update_merchants import *
# Merchant.objects.filter(universe_name__isnull=True).count()
def update_merchant():
    try:
        connection_to_mw = psycopg2.connect(
            user=str(settings.DB_MW_USER),
            password=str(settings.DB_MW_PASSWORD),
            host=str(settings.DB_MW_HOST),
            port=str(settings.DB_MW_PORT),
            database=str(settings.DB_MW_NAME),
        )

        cursor_to_mw = connection_to_mw.cursor()

        merchants_query = """SELECT \
                                offer.id AS mw_offer_id, \
                                offer.visible, \
                                offer.title, \
                                offer.odoo_pricelist_id AS odoo_offer_id, \
                                offer.average_rating, \
                                conciergerie.id AS mw_neighborhood_id, \
                                conciergerie.odoo_conciergerie_id, \
                                category.title, \
                                offer.tags \
                            FROM \
                                societymanagement.service AS offer \
                            JOIN \
                                societymanagement.category ON offer.category_id = societymanagement.category.id \
                            JOIN \
                                societymanagement.conciergerie ON societymanagement.category.conciergerie_id = societymanagement.conciergerie.id \
                            WHERE \
                                conciergerie.id NOT IN (1, 3, 4, 105) AND conciergerie.id IS NOT NULL;"""

        cursor_to_mw.execute(merchants_query)
        merchants_from_mw = cursor_to_mw.fetchall()

        # Update Merchant
        for row in merchants_from_mw:
            try:
                merchant = Merchant.objects.filter(mw_offer_id=row[0])
                counter = merchant.count()

                tags = str(row[8]).split("///")

                if counter == 0:
                    Merchant(
                        name=row[2],
                        neighborhood=Neighborhood.objects.get(mw_id=row[5]),
                        mw_offer_id=row[0],
                        odoo_offer_id=row[3],
                        universe_name=row[7],
                        rating=row[4],
                        active=row[1],
                        tags=tags,
                        rating_number=Order.objects.filter(mw_offer_id=row[0]).exclude(rating=0).count()
                    ).save()

                elif counter == 1:
                    merchant_to_update = Merchant.objects.get(mw_offer_id=row[0])

                    if merchant_to_update.active != row[1]:
                        email = EmailMessage(
                            '[FERMETURE / OUVERTURE COMMERÇANT]',
                            str(
                                str("Merchant:" + merchant_to_update.name)
                                + str("\n")
                                + str("\n")
                                + str("\n")
                                + str("Active: " + str(row[1]))
                                + str("\n")
                                + str("\n")
                                + str("\n")
                                + str("Neighborhood:" + str(merchant_to_update.neighborhood.name))
                                + str("\n")
                                + str("\n")
                                + str("\n")
                                + str("Universe Name: " + str(merchant_to_update.universe_name))
                            ),
                            'Please <contact@pleaseapp.com>',
                            ['francois.rabier@pleaseapp.com'],
                        )
                        email.send()

                    merchant_to_update.name = row[2]
                    merchant_to_update.neighborhood = Neighborhood.objects.get(mw_id=row[5])
                    merchant_to_update.mw_offer_id = row[0]
                    merchant_to_update.odoo_offer_id = row[3]
                    merchant_to_update.universe_name = row[7]
                    merchant_to_update.rating = row[4]
                    merchant_to_update.active = row[1]
                    merchant_to_update.tags = tags
                    merchant_to_update.rating_number = Order.objects.filter(mw_offer_id=merchant_to_update.mw_offer_id).exclude(rating=0).count()
                    merchant_to_update.save()

                elif counter > 1:
                    merchant.delete()

                    Merchant(
                        name=row[2],
                        neighborhood=Neighborhood.objects.get(mw_id=row[5]),
                        mw_offer_id=row[0],
                        odoo_offer_id=row[3],
                        universe_name=row[7],
                        rating=row[4],
                        active=row[1],
                        tags=tags,
                        rating_number=Order.objects.filter(mw_offer_id=row[0]).exclude(rating=0).count()
                    ).save()

            except:
                print("ERROR: etl not updating merchant - " + str(sys.exc_info()))

        # Close Cursor and Connection to MW DB
        cursor_to_mw.close()
        connection_to_mw.close()

    except:
        print("ERROR: not updating merchant - " + str(sys.exc_info()))
        # Close Cursor and Connection to MW DB
        if connection_to_mw:
            cursor_to_mw.close()
            connection_to_mw.close()

    return


def import_etl_update_merchant():
    log_script(name="import_etl_update_merchant", status="s")
    try:
        update_merchant()
        log_script(name="import_etl_update_merchant", status="d")
    except:
        print("ERROR: ETL UPDATE MERCHANT FAILED - " + str(sys.exc_info()))


# from please_marketing_etl.etl_update_merchants import *
# Merchant.objects.filter(universe_name__isnull=True).count()
def update_merchant_open():
    try:
        # Update Merchant Open
        for merchant in Merchant.objects.filter(active=True):
            try:
                url = str("https://mw.please-it.com/next-mw/api/public/website/services/menu/" + str(merchant.mw_offer_id))
                response = requests.request("GET", url).json()

                if response.get("status") is "OPEN":
                    merchant.open = True
                    merchant.save()

                else:
                    merchant.open = False
                    merchant.save()

            except:
                print("ERROR: etl not updating merchant - " + str(sys.exc_info()))

    except:
        print("ERROR: not updating merchant - " + str(sys.exc_info()))

    return


def import_etl_update_merchant_open():
    log_script(name="import_etl_update_merchant_open", status="s")
    try:
        update_merchant_open()
        log_script(name="import_etl_update_merchant_open", status="d")
    except:
        print("ERROR: ETL UPDATE MERCHANT OPEN FAILED - " + str(sys.exc_info()))
