# -*- coding: utf-8 -*-

from please_marketing_script_execution.log_script import log_script
from please_marketing_app.main_scripts.google_api import geocoding
from please_marketing_app.models import DeliveryManLead
from django.conf import settings
import psycopg2.extensions
import psycopg2
import json
import sys
import requests


# from please_marketing_etl.etl_update_delivery_men_leads import *
def update_delivery_men_leads():
    try:
        connection_to_please_website = psycopg2.connect(
            user=str(settings.DB_PP_USER),
            password=str(settings.DB_PP_PASSWORD),
            host=str(settings.DB_PP_HOST),
            port=str(settings.DB_PP_PORT),
            database=str(settings.DB_PP_NAME),
        )

        cursor_to_pp = connection_to_please_website.cursor()

        query = """SELECT \
                                delivery_man.first_name, \
                                delivery_man.last_name, \
                                delivery_man.email, \
                                delivery_man.phone, \
                                delivery_man.city, \
                                delivery_man.message \
                               
                            FROM \
                                please_website_app_logcontactformdelivery AS delivery_man \
                """

        cursor_to_pp.execute(query)
        delivery_men = cursor_to_pp.fetchall()

        # Update Merchant
        for row in delivery_men:
            try:
                delivery_man = DeliveryManLead.objects.filter(email=row[2])
                counter = delivery_man.count()

                if counter == 0:
                    DeliveryManLead(
                        first_name=row[0],
                        last_name=row[1],
                        email=row[2],
                        phone=row[3],
                        city=row[4],
                        message=row[5],
                    ).save()

            except:
                print("ERROR: etl not saved delivery man lead from pp - " + str(sys.exc_info()))

        # Close Cursor and Connection to MW DB
        cursor_to_pp.close()
        connection_to_please_website.close()

    except:
        print("ERROR: etl not saved delivery man lead from pp - " + str(sys.exc_info()))
        # Close Cursor and Connection to MW DB
        if connection_to_please_website:
            cursor_to_pp.close()
            connection_to_please_website.close()

    return


def set_formatted_address():

    for dml in DeliveryManLead.objects.filter(formatted_address__isnull=True):
        print(dml.city)
        try:
            results = geocoding(city=dml.city)

            dml.formatted_address = results[0]
            dml.lat = results[1]
            dml.lng = results[2]
            dml.city = dml.city if not results[3] else results[3]
            dml.save()

        except:
            print("ERROR: SET ADDRESS FOR DELIVERY MEN LEADS FAILED - " + str(sys.exc_info()))
    return


def import_update_delivery_men_leads():
    log_script(name="import_update_delivery_men_leads", status="s")
    try:
        update_delivery_men_leads()
        set_formatted_address()
        log_script(name="import_update_delivery_men_leads", status="d")
    except:
        print("ERROR: ETL UPDATE DELIVERY MEN LEADS FAILED - " + str(sys.exc_info()))
