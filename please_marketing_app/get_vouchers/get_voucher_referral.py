# -*- coding: utf-8 -*-
import pprint
import xmlrpc.client
import xmlrpc.server
import ssl
from please_marketing_app.models import VoucherCode
from django.conf import settings
import sys
import datetime


def get_one_voucher_referral(
        customer,
        voucher_name,
        voucher_validity,
        voucher_value,
        voucher_val_type,
        voucher_code,
        minimum_cart_amount,
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
                  'data': {'name': voucher_name,                  # str Nom du coupon dans Odoo apparaît dans la ligne de commande
                           'voucher_validity': voucher_validity,  # int validité du coupon en jours
                           'expiry_date': '',                     # Don't Use
                           'voucher_value': voucher_value,        # int Valeur du coupon
                           'voucher_val_type': voucher_val_type,  # str Type de valeur 'amount' ou 'percent'
                           'voucher_code': voucher_code,          # str Code du coupon sur 15 caractères ou 0 pour une génération automatique
                           'customer_id': '',                     # int Id Odoo du client
                           'first_order_only': False,             # bool Usage unique du coupon
                           'first_customer_order': True,          # bool Usage pour une première commande
                           'pricelist_id': False,                 # int Id Odoo de l'offre ou False
                           'total_available': -1,                 # int Nombre de coupons disponibles -1 : infini
                           'minimum_cart_amount': float(minimum_cart_amount),               # float
                           },
                  }

        voucher_data = sock.execute(dbname, uid, pwd, 'sale.order', 'get_marketing_voucher', params)

        pprint.pprint(voucher_data)

        if (voucher_data[0].get("voucher_code") is not None) or (voucher_data[0].get("voucher_code") is not ""):

            r_voucher_code = voucher_data[0].get("voucher_code")

            return r_voucher_code

    except:
        print("ERROR: Failed to get referral voucher from Odoo for user " + str(customer.email) + " - " + str(
            sys.exc_info()))

        return
