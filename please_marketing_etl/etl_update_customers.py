# -*- coding: utf-8 -*-

from please_marketing_script_execution.log_script import log_script
from please_marketing_app.models import Order, Customer, Merchant, Neighborhood
from django.conf import settings
import psycopg2.extensions
import psycopg2
import json
import sys
from concurrent.futures import ThreadPoolExecutor


# from please_marketing_etl.etl_update_customers import *
def update_customer_marketing():
    try:
        exclusion_list = []

        for cus in Customer.objects.filter(odoo_user_id__isnull=False, marketing=False):
            exclusion_list.append(cus.odoo_user_id)

        connection_to_mw = psycopg2.connect(
            user=str(settings.DB_MW_USER),
            password=str(settings.DB_MW_PASSWORD),
            host=str(settings.DB_MW_HOST),
            port=str(settings.DB_MW_PORT),
            database=str(settings.DB_MW_NAME),
        )

        cursor_to_mw = connection_to_mw.cursor()

        customers_query = """SELECT \
                                user_main.odoo_id, \
                                user_main.email, \
                                user_simple.marketing_subscription \
                            FROM usermanagement.user AS user_main \
                            JOIN usermanagement.user_simple AS user_simple ON user_simple.id = user_main.id \
                            WHERE user_simple.marketing_subscription IS FALSE \
                            AND user_main.odoo_id NOT IN """ + str(tuple(exclusion_list)) + """ \
                            ORDER BY creation_date DESC;"""

        cursor_to_mw.execute(customers_query)
        customers_from_mw = cursor_to_mw.fetchall()

        print(customers_from_mw)

        # Update Customer
        for row in customers_from_mw:
            try:
                customer = Customer.objects.filter(odoo_user_id=row[0], email=row[1]).first()
                if customer:
                    if customer.marketing is False:
                        pass
                    else:
                        customer.marketing = row[2]
                        customer.save()
                else:
                    print("WARNING: no matching user for: " + str(row[1]))
            except:
                print("ERROR: not updating marketing subscription for " + str(sys.exc_info()))

        # Close Cursor and Connection to MW DB
        cursor_to_mw.close()
        connection_to_mw.close()

    except:
        print("ERROR: not updating marketing subscription - " + str(sys.exc_info()))
        # Close Cursor and Connection to MW DB
        if connection_to_mw:
            cursor_to_mw.close()
            connection_to_mw.close()

    return


def import_etl_update_customers():
    log_script(name="import_etl_update_customers", status="s")
    try:
        update_customer_marketing()
        log_script(name="import_etl_update_customers", status="d")
    except:
        print("ERROR: ETL UPDATE CUSTOMERS FAILED - " + str(sys.exc_info()))

    return


def update_customer_phone():

    def insert_raw(row):
        print(row)
        try:
            if Customer.objects.filter(odoo_user_id=row[0]).count() == 1:

                customer = Customer.objects.get(odoo_user_id=row[0])

                customer.phone = row[2]
                customer.save()

        except:
            print("ERROR: not updating phone for " + str(sys.exc_info()))

        return

    try:
        connection_to_mw = psycopg2.connect(
            user=str(settings.DB_MW_USER),
            password=str(settings.DB_MW_PASSWORD),
            host=str(settings.DB_MW_HOST),
            port=str(settings.DB_MW_PORT),
            database=str(settings.DB_MW_NAME),
        )

        cursor_to_mw = connection_to_mw.cursor()

        customers_query = """SELECT \
                                user_main.odoo_id, \
                                user_main.email, \
                                user_main.mobile_number \
                            FROM usermanagement.user AS user_main \
                            WHERE user_main.odoo_conciergerie_id NOT IN (1, 2, 10) \
                            ORDER BY creation_date DESC;"""

        cursor_to_mw.execute(customers_query)
        customers_from_mw = cursor_to_mw.fetchall()

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(insert_raw, customers_from_mw)

        # Close Cursor and Connection to MW DB
        cursor_to_mw.close()
        connection_to_mw.close()

    except:
        print("ERROR: not updating phone - " + str(sys.exc_info()))
        # Close Cursor and Connection to MW DB
        if connection_to_mw:
            cursor_to_mw.close()
            connection_to_mw.close()

    return


def import_etl_update_customers_phone():
    log_script(name="import_etl_update_customers_phone", status="s")
    try:
        update_customer_phone()
        log_script(name="import_etl_update_customers_phone", status="d")
    except:
        print("ERROR: ETL UPDATE CUSTOMERS PHONE FAILED - " + str(sys.exc_info()))

    return


# from please_marketing_etl.etl_update_customers import *
def compare_users():

    connection_to_mw = psycopg2.connect(
        user=str(settings.DB_MW_USER),
        password=str(settings.DB_MW_PASSWORD),
        host=str(settings.DB_MW_HOST),
        port=str(settings.DB_MW_PORT),
        database=str(settings.DB_MW_NAME),
    )

    cursor_to_mw = connection_to_mw.cursor()

    connection_to_odoo = psycopg2.connect(
        user=str(settings.DB_ODOO_USER),
        password=str(settings.DB_ODOO_PASSWORD),
        host=str(settings.DB_ODOO_HOST),
        port=str(settings.DB_ODOO_PORT),
        database=str(settings.DB_ODOO_NAME),
    )

    cursor_to_odoo = connection_to_odoo.cursor()

    mw_users_query = """SELECT
                            odoo_id
                                FROM usermanagement.user;"""

    odoo_users_query = """SELECT
                        client.id
                    FROM res_partner AS client;"""

    # MW Cursor Exec
    cursor_to_mw.execute(mw_users_query)
    customers_from_mw = cursor_to_mw.fetchall()
    cursor_to_mw.close()
    connection_to_mw.close()

    # Odoo Cursor Exec
    cursor_to_odoo.execute(odoo_users_query)
    customers_from_odoo = cursor_to_odoo.fetchall()
    cursor_to_odoo.close()
    connection_to_odoo.close()

    # AUB - ANB
    AUB = set(customers_from_mw).union(set(customers_from_odoo))
    ANB = set(customers_from_mw).intersection(set(customers_from_odoo))
    not_matching_customers = AUB.difference(ANB)
    print("Nombre de unmatch : " + str(len(not_matching_customers)))

    for cus in not_matching_customers:
        customer = Customer.objects.filter(odoo_user_id=cus[0]).first()
        if customer:
            print(str(cus[0]), customer)

    return
