# -*- coding: utf-8 -*-
import pprint
import xmlrpc.client
import xmlrpc.server
import ssl
from please_marketing_app.models import VoucherCode
from django.conf import settings
import sys
import datetime


def get_one_voucher_reward(
        customer,
        notification_type,
        voucher_name,
        voucher_validity,
        voucher_value,
        voucher_val_type,
        voucher_code,
        first_order_only,
        first_customer_order,
        pricelist_id,
        minimum_cart_amount,
        total_available,
        ):

    try:

        context = ssl.SSLContext()

        username = str(settings.ODOO_USERNAME)
        pwd = str(settings.ODOO_PASSWORD)
        dbname = str(settings.ODOO_DB_NAME)
        url = str(settings.ODOO_URL)

        # Get the uid
        sock_common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common', context=context)
        uid = sock_common.login(dbname, username, pwd)
        sock = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object', context=context)

        # Input values
        params = {
                  'partner_id': 1,
                  'partner_hash': str(settings.ODOO_PARTNER_HASH),
                  'data': {'name': voucher_name,                   # str Nom du coupon dans Odoo apparaît dans la ligne de commande
                           'voucher_validity': voucher_validity,   # int validité du coupon en jours
                           'expiry_date': '',                      # Don't Use
                           'voucher_value': voucher_value,         # int Valeur du coupon
                           'voucher_val_type': voucher_val_type,   # str Type de valeur 'amount' ou 'percent'
                           'voucher_code': voucher_code,           # str Code du coupon sur 15 caractères ou 0 pour une génération automatique
                           'customer_id': customer.odoo_user_id,   # int Id Odoo du client
                           'first_order_only': first_order_only,   # bool Usage unique du coupon
                           'first_customer_order': first_customer_order,          # bool Usage pour une première commande
                           'pricelist_id': pricelist_id,           # int Id Odoo de l'offre ou False
                           'minimum_cart_amount': float(minimum_cart_amount),       # Float
                           'total_available': int(total_available),              # Int
                           },
                  }

        voucher_data = sock.execute(dbname, uid, pwd, 'sale.order', 'get_marketing_voucher', params)

        pprint.pprint(voucher_data)

        if (voucher_data[0].get("voucher_code") is not None) or (voucher_data[0].get("voucher_code") is not ""):

            VoucherCode(
                customer=customer,
                code=voucher_data[0].get("voucher_code"),
                name=voucher_name,
                voucher_type=voucher_val_type,
                value=voucher_value,
                expiry_date=datetime.datetime.strptime(voucher_data[0].get("voucher_validity"), '%Y-%m-%d %H:%M:%S'),
                notification_type=notification_type
            ).save()

            r_customer = customer
            r_voucher_code = voucher_data[0].get("voucher_code")
            r_voucher_name = voucher_name
            r_voucher_type = voucher_val_type
            r_value = voucher_value
            r_expiry_date = datetime.datetime.strptime(voucher_data[0].get("voucher_validity"), '%Y-%m-%d %H:%M:%S')
            r_notification_type = notification_type
            r_pricelist_id = pricelist_id

            return r_customer, r_voucher_code, r_voucher_name, r_voucher_type, r_value, r_expiry_date, r_notification_type, r_pricelist_id

    except:
        print("ERROR: Failed to get voucher from Odoo for user " + str(customer.email) + " - " + str(
            sys.exc_info()))

        return
