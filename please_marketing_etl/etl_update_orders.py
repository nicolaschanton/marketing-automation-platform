# -*- coding: utf-8 -*-

from please_marketing_script_execution.log_script import log_script
from please_marketing_app.models import Order, Customer, Merchant, Neighborhood
from django.conf import settings
import psycopg2.extensions
import psycopg2
import json
import sys
from concurrent.futures import ThreadPoolExecutor


# from please_marketing_etl.etl_update_orders import *
def update_order_date():

    def insert_raw(row):
        print(row)
        try:
            if Order.objects.filter(odoo_order_id=row[0]).count() == 1:

                order = Order.objects.get(odoo_order_id=row[0])

                order.order_date = row[1]
                order.save()

        except:
            print("ERROR: not updating order_date for " + str(sys.exc_info()))

        return

    try:
        connection_to_odoo = psycopg2.connect(
            user=str(settings.DB_ODOO_USER),
            password=str(settings.DB_ODOO_PASSWORD),
            host=str(settings.DB_ODOO_HOST),
            port=str(settings.DB_ODOO_PORT),
            database=str(settings.DB_ODOO_NAME),
        )

        cursor_to_odoo = connection_to_odoo.cursor()

        orders_query = """SELECT \
                                so.id AS odoo_order_id, \
                                so.create_date AS order_date \
                            FROM sale_order AS so \
                            WHERE so.partner_id IS NOT NULL \
                            AND so.state NOT IN ('draft', 'authorized', 'authorization_progress', 'payment_progress', 'progress', 'cancel', 'litige', 'shipping_except') \
                            AND so.neighborhood_id NOT IN (1,2,10);"""

        cursor_to_odoo.execute(orders_query)
        orders_from_odoo = cursor_to_odoo.fetchall()

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(insert_raw, orders_from_odoo)

        # Close Cursor and Connection to Odoo DB
        cursor_to_odoo.close()
        connection_to_odoo.close()

    except:
        print("ERROR: not updating order_date - " + str(sys.exc_info()))
        # Close Cursor and Connection to MW DB
        if connection_to_odoo:
            cursor_to_odoo.close()
            connection_to_odoo.close()

    return


def import_etl_update_orders():
    log_script(name="import_etl_update_orders", status="s")
    try:
        update_order_date()
        log_script(name="import_etl_update_orders", status="d")
    except:
        print("ERROR: ETL UPDATE ORDERS FAILED - " + str(sys.exc_info()))

    return
