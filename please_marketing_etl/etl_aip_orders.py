# -*- coding: utf-8 -*-

from please_marketing_script_execution.log_script import log_script
from please_marketing_app.models import Order, Customer, Merchant, Neighborhood, SmsAuthorizationInProgress, SmsHistory
from django.conf import settings
import psycopg2.extensions
import psycopg2
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from please_marketing_app.get_vouchers.get_voucher_activate_rookies import get_one_voucher
from twilio.rest import Client
import emoji
from please_marketing_app.main_scripts.utilities import get_good_sender
from datetime import datetime, timedelta
import random


# from please_marketing_etl.etl_aip_orders import *
# customer = Customer.objects.get(email="melachat@gmail.com")
def send_please_support_alert(customer, odoo_order_id):
    try:
        # Your Account Sid and Auth Token from twilio.com/user/account
        account_sid = str(settings.TWILIO_SID)
        auth_token = str(settings.TWILIO_TOKEN)
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            "+33768740480",
            body=str(
                str("PROBLÈME PAYBOX")
                + str("\n")
                + str("Client : " + str(customer.email))
                + str(" | ")
                + str(customer.first_name) + str(" ") + str(customer.last_name)
                + str(" | ")
                + str(customer.phone)
                + str("\n")
                + str("Odoo Order Id : " + str(odoo_order_id))
            ),
            from_="Please"
        )

        print(message.sid, message.date_created.date, message.body)

        print("SUCCES: SMS Alert properly sent for please_support")

    except (KeyError, AttributeError):
        print("ERROR: Twilio API Error - Message Alert for please_support SMS not sent")
    return


def send_sms_10(customer):
    try:
        res_voucher = get_one_voucher(
            customer=customer,
            voucher_name=str("Coupon relance problème paiement - " + customer.email),
            notification_type="issue_aip_10",
            voucher_code=0,
            first_customer_order=False,
            first_order_only=True,
            voucher_value=10,
            voucher_val_type='amount',
            pricelist_id=False,
            voucher_validity=2,
            minimum_cart_amount=15,
        )

        voucher_code = res_voucher[1]

        # Your Account Sid and Auth Token from twilio.com/user/account
        account_sid = str(settings.TWILIO_SID)
        auth_token = str(settings.TWILIO_TOKEN)
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            str(customer.phone),
            body=str(
                str(customer.first_name)
                + ", malheureusement votre commande a été annulée suite à un refus bancaire !"
                + str("\n")
                + str("\n")
                + str("10€ offerts pendant 48h avec le code " + voucher_code)
                + str(" pour retenter l'expérience Please !")
            ),
            from_=get_good_sender(customer=customer)
        )

        print(message.sid, message.date_created.date, message.body)

        SmsHistory(
            customer=customer,
            content=message.body,
            send_date=datetime.now(),
            sms_type="issue_aip_10",
        ).save()

        print("SUCCES: SMS properly sent for issue_aip to user " + customer.email + " - " + customer.phone)

    except (KeyError, AttributeError):
        print("ERROR: Twilio API Error - Message for issue_aip_10 SMS not sent")

    return


def treat_aip_orders_10():

    def sms_aip_treatment_10(row):
        print(row)
        try:
            if SmsAuthorizationInProgress.objects.filter(odoo_order_id=row[0]).count() == 0:

                customer = Customer.objects.get(odoo_user_id=row[1])

                send_sms_10(customer=customer)

                SmsAuthorizationInProgress(
                    customer=customer,
                    odoo_order_id=int(row[0]),
                    sms_type="treat_aip_orders_10",
                ).save()

                send_please_support_alert(customer=customer, odoo_order_id=row[0])

            elif SmsAuthorizationInProgress.objects.filter(odoo_order_id=row[0]).count() == 1:
                customer = Customer.objects.get(odoo_user_id=row[1])
                print("aip_orders_10_sms already sent to " + customer.email)

        except:
            print("ERROR: not sending sms for issue_aip_10 for " + str(sys.exc_info()))

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

        exclusion_list = []
        for cus in SmsAuthorizationInProgress.objects.all():
            exclusion_list.append(cus.odoo_order_id)

        orders_query = """SELECT
                                so.id,
                                so.partner_id AS odoo_user_id,
                                so.name AS commande
                            FROM
                                sale_order so
                                JOIN account_voucher voucher ON so.voucher_id = voucher.id
                                JOIN please_payment_request request ON voucher.id = request.voucher_id
                            WHERE
                                so.state = 'authorization_progress'
                                AND so.voucher_id IS NOT NULL
                                AND request.state IS NULL
                                AND numtrans IS NULL
                                AND numappel IS NULL
                                AND so.create_date > (now() - INTERVAL '3600 seconds')
                                AND (so.create_date + INTERVAL '30 seconds') < now();"""

        cursor_to_odoo.execute(orders_query)
        orders_from_odoo = cursor_to_odoo.fetchall()

        # Beginning of sending aip scripts
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(sms_aip_treatment_10, orders_from_odoo)

        # Close Cursor and Connection to Odoo DB
        cursor_to_odoo.close()
        connection_to_odoo.close()

    except:
        print("ERROR: not updating issue_aip_10 - " + str(sys.exc_info()))
        # Close Cursor and Connection to MW DB
        if connection_to_odoo:
            cursor_to_odoo.close()
            connection_to_odoo.close()

    return


def send_sms(customer):

    coin = random.randint(0, 1)

    if coin == 0:
        try:
            # Your Account Sid and Auth Token from twilio.com/user/account
            account_sid = str(settings.TWILIO_SID)
            auth_token = str(settings.TWILIO_TOKEN)
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                str(customer.phone),
                body=str(
                    str(customer.first_name)
                    + str(", votre commande n'a pas été finalisée.")
                    + str("\n")
                    + str("Cliquez ici pour la valider : http://onelink.to/pleaseapp !")
                ),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.now(),
                sms_type="abandoned_cart_aip",
            ).save()

            print("SUCCES: SMS properly sent for abandoned_cart_aip to user " + customer.email + " - " + customer.phone)

        except (KeyError, AttributeError):
            print("ERROR: Twilio API Error - Message for abandoned_cart_aip SMS not sent")

    elif coin == 1:
        res_voucher = get_one_voucher(
            customer=customer,
            voucher_name=str("Coupon panier abandonné - " + customer.email),
            notification_type="abandoned_cart_aip_5",
            voucher_code=0,
            first_customer_order=False,
            first_order_only=True,
            voucher_value=5,
            voucher_val_type='amount',
            pricelist_id=False,
            voucher_validity=2,
            minimum_cart_amount=15,
        )

        voucher_code = res_voucher[1]

        try:
            # Your Account Sid and Auth Token from twilio.com/user/account
            account_sid = str(settings.TWILIO_SID)
            auth_token = str(settings.TWILIO_TOKEN)
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                str(customer.phone),
                body=str(
                    str(customer.first_name)
                    + str(", votre commande n'a pas été finalisée, bénéficiez de 5€ offerts jusqu'à demain avec le code ")
                    + str(voucher_code)
                    + str(" !")
                    + str("\n")
                    + str("Cliquez ici pour la valider : http://onelink.to/pleaseapp !")
                ),
                from_=get_good_sender(customer=customer)
            )

            print(message.sid, message.date_created.date, message.body)

            SmsHistory(
                customer=customer,
                content=message.body,
                send_date=datetime.now(),
                sms_type="abandoned_cart_aip_5",
            ).save()

            print("SUCCES: SMS properly sent for abandoned_cart_aip to user " + customer.email + " - " + customer.phone)

        except (KeyError, AttributeError):
            print("ERROR: Twilio API Error - Message for abandoned_cart_aip SMS not sent")

    return


def treat_aip_orders():

    def sms_aip_treatment(row):
        print(row)
        try:
            if SmsAuthorizationInProgress.objects.filter(odoo_order_id=row[0]).count() == 0:

                customer = Customer.objects.get(odoo_user_id=row[1])

                send_sms(customer=customer)

                SmsAuthorizationInProgress(
                    customer=customer,
                    odoo_order_id=int(row[0]),
                    sms_type="treat_aip_orders",
                ).save()

            elif SmsAuthorizationInProgress.objects.filter(odoo_order_id=row[0]).count() == 1:
                customer = Customer.objects.get(odoo_user_id=row[1])
                print("aip_orders_sms already sent to " + customer.email)

        except:
            print("ERROR: not sending sms for aip for " + str(sys.exc_info()))

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

        exclusion_list = []
        for cus in SmsAuthorizationInProgress.objects.all():
            exclusion_list.append(cus.odoo_order_id)

        orders_query = """SELECT
                                so.id,
                                so.partner_id AS odoo_user_id,
                                so.name AS commande
                            FROM
                                sale_order so
                            WHERE
                                so.state = 'authorization_progress'
                                AND so.create_date > (now() - INTERVAL '3600 seconds')
                                AND (so.create_date + INTERVAL '360 seconds') < now();"""

        cursor_to_odoo.execute(orders_query)
        orders_from_odoo = cursor_to_odoo.fetchall()

        # Beginning of sending aip scripts
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(sms_aip_treatment, orders_from_odoo)

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


# from please_marketing_etl.etl_aip_orders import *
# customer = Customer.objects.get(email="melachat@gmail.com")
def execute_aip_orders():
    try:
        treat_aip_orders_10()
        treat_aip_orders()
    except:
        print("ERROR: ETL AIP ORDERS FAILED - " + str(sys.exc_info()))

    return
