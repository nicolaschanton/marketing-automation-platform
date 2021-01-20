# -*- coding: utf-8 -*-

from please_marketing_script_execution.log_script import log_script
from please_marketing_app.models import Order, Customer, Merchant
import requests
from django.conf import settings
from datetime import datetime as DT
import psycopg2.extensions
import psycopg2
import json
import traceback
import sys
from concurrent.futures import ThreadPoolExecutor
import uuid


# from please_marketing_etl.etl_regular import *

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

NEIGHBORHOODS = {}
PRICELISTS = {}
CATEGORIES = {}
SUPPLIERS = {}
STATS_EMAILS = {}


class etl_market(object):
    def connect_to_database(self):
        market_db_host = str(settings.DB_HOST)
        market_db_login = str(settings.DB_USER)
        market_db_pwd = str(settings.DB_PASSWORD)
        market_db_name = str(settings.DB_NAME)
        conn_string = "host='" + market_db_host + "' dbname='" + market_db_name + "' user='" + market_db_login + "' password='" + market_db_pwd + "'"
        self.cnx = psycopg2.connect(conn_string)

    def connect_to_mw(self):
        mw_db_host = str(settings.DB_MW_HOST)
        mw_db_login = str(settings.DB_MW_USER)
        mw_db_pwd = str(settings.DB_MW_PASSWORD)
        mw_db_name = str(settings.DB_MW_NAME)
        conn_string = "host='" + mw_db_host + "' dbname='" + mw_db_name + "' user='" + mw_db_login + "' password='" + mw_db_pwd + "'"
        self.mw_cnx = psycopg2.connect(conn_string)

    def connect_to_odoo(self):
        odoo_db_host = str(settings.DB_ODOO_HOST)
        odoo_db_login = str(settings.DB_ODOO_USER)
        odoo_db_pwd = str(settings.DB_ODOO_PASSWORD)
        odoo_db_name = str(settings.DB_ODOO_NAME)
        conn_string = "host='" + odoo_db_host + "' dbname='" + odoo_db_name + "' user='" + odoo_db_login + "' password='" + odoo_db_pwd + "'"
        self.odoo_cnx = psycopg2.connect(conn_string)

    def get_mw_data(self):
        self.connect_to_mw()
        cur = self.mw_cnx.cursor()

        # Récupération des quartiers
        sql_mw_neighb = "SELECT odoo_conciergerie_id, id FROM societymanagement.conciergerie;"
        cur.execute(sql_mw_neighb)
        res = cur.fetchall()

        cur_market = self.cnx.cursor()
        for r in res:
            NEIGHBORHOODS[r[0]] = r[1]
            cur_market.execute("UPDATE please_marketing_app_neighborhood SET mw_id=%s WHERE odoo_id=%s;" % (r[1], r[0]))
        self.cnx.commit()

        # Récupération des offres
        sql_mw_pricelist = "SELECT odoo_pricelist_id, id FROM societymanagement.service;"
        cur.execute(sql_mw_pricelist)
        res = cur.fetchall()

        for r in res:
            PRICELISTS[r[0]] = r[1]

        # Récupération des catégories
        sql_mw_category = "SELECT odoo_category_id, id FROM societymanagement.category;"
        cur.execute(sql_mw_category)
        res = cur.fetchall()

        for r in res:
            CATEGORIES[r[0]] = r[1]

        # Récupération des suppliers + première offre active du commerçant
        sql_mw_suppliers = "SELECT \
                                DISTINCT \
                                user_pro.odoo_id, \
                                user_pro.id, \
                                service.id as mw_offer_id, \
                                service.odoo_pricelist_id as odoo_offer_id \
                            FROM societymanagement.service service \
                            JOIN societymanagement.service_user rel ON service.id = rel.service_id \
                            JOIN usermanagement.user user_pro ON rel.user_id = user_pro.id \
                            ORDER BY 1,2;"
        cur.execute(sql_mw_suppliers)
        res = cur.fetchall()

        for r in res:
            if not r[0] in SUPPLIERS:
                SUPPLIERS[r[0]] = [r[1], r[2], r[3]]

        self.mw_cnx.close()

    def disconnect_to_database(self):
        self.cnx.close()

    def get_django_objetc_id(self, key, value, fields):
        sql_query = ''
        dic_values = {'fields': fields, 'values': value}
        if key == 'neighborhood':
            sql_query = "SELECT %(fields)s FROM please_marketing_app_neighborhood WHERE odoo_id=%(values)s;"
        elif key == 'customer':
            sql_query = "SELECT %(fields)s FROM please_marketing_app_customer WHERE odoo_user_id=%(values)s;"

        if sql_query:
            cur = self.cnx.cursor()
            cur.execute(sql_query % dic_values)
            res = cur.fetchall()
            if res:
                return res[0][0]
            else:
                return 'NULL'

        else:
            return False

    def get_neighborhoods(self):
        self.connect_to_odoo()
        cur = self.odoo_cnx.cursor()
        cur.execute('SELECT id, code FROM neighborhood_neighborhood WHERE active = TRUE AND id NOT IN (1,2);')
        res_neighborhood = cur.fetchall()

        lst_neighborhood = []

        for n in res_neighborhood:
            dic_neighborhood = {'odoo_id': n[0],
                                'name': n[1]
                                }

            lst_neighborhood.append(dic_neighborhood)

        return lst_neighborhood

    def get_credit_cards(self, partner_id):
        cur = self.odoo_cnx.cursor()
        cur.execute('SELECT card_type FROM credit_card WHERE partner_id = %(partner_id)s;' % {'partner_id': partner_id})
        res_cb = cur.fetchall()

        lst_cb = []
        for r in res_cb:
            if not r[0] in lst_cb:
                lst_cb.append(r[0])

        return str(lst_cb).replace('[', '{').replace(']', '}').replace("u'", "").replace("'", "")

    def get_customers(self):

        exclusion_list = []

        for cus in Customer.objects.filter(odoo_user_id__isnull=False):
            exclusion_list.append(cus.odoo_user_id)

        print(str(len(exclusion_list)))

        # Récupération de tous les clients de la base
        cur = self.odoo_cnx.cursor()
        cur.execute(str('SELECT \
                        client.id, \
                        client.firstname, \
                        client.lastname, \
                        client.email, \
                        client.mobile, \
                        client.street, \
                        client.zip, \
                        client.city, \
                        quartier.id, \
                        client.create_date, \
                        client.dev \
                    FROM res_partner client \
                    JOIN neighborhood_neighborhood quartier ON client.neighborhood_id = quartier.id \
                    WHERE client.active = TRUE AND client.customer = TRUE AND client.id NOT IN ' + str(tuple(exclusion_list)) + '\
                    AND client.neighborhood_id NOT IN (1,2,10) \
                    AND quartier.active = TRUE \
                    ORDER BY quartier.id, client.id;'))
        res_customers = cur.fetchall()

        lst_customers = []

        for r in res_customers:
            print(r)
            dic_customer = {}
            dic_customer['odoo_user_id'] = r[0]
            dic_customer['first_name'] = r[1]
            dic_customer['last_name'] = r[2]
            dic_customer['email'] = r[3]
            dic_customer['phone'] = r[4]
            dic_customer['street'] = r[5]
            dic_customer['zip'] = r[6]
            dic_customer['city'] = r[7]
            dic_customer['neighborhood'] = r[8]
            dic_customer['cb'] = self.get_credit_cards(r[0])
            dic_customer['sign_up_date'] = r[9]
            dic_customer['signed_up'] = True
            dic_customer['dev'] = r[10]
            lst_customers.append(dic_customer)

        return lst_customers

    def get_archived_customers(self):
        # Récupération de tous les clients désinscrits de la base de données
        cur = self.odoo_cnx.cursor()
        cur.execute('SELECT \
                        client.id \
                    FROM res_partner client \
                    JOIN neighborhood_neighborhood quartier ON client.neighborhood_id = quartier.id \
                    WHERE client.active = FALSE AND client.neighborhood_id NOT IN (1,2,10) AND quartier.active = TRUE \
                    AND client.customer = TRUE \
                    ORDER BY client.id;')
        res_customers = cur.fetchall()

        lst_customers = []

        for r in res_customers:
            dic_customer = {}
            dic_customer['odoo_user_id'] = r[0]
            lst_customers.append(dic_customer)

        return lst_customers

    def update_archived_customers(self, archived_customers):
        # Mise à jour des clients désinscrits
        sql_update = "UPDATE please_marketing_app_customer SET archived=TRUE, marketing=FALSE WHERE odoo_user_id = %(odoo_user_id)s;"
        cur = self.cnx.cursor()
        try:
            for ar_customer in archived_customers:
                cur.execute(sql_update % {'odoo_user_id': ar_customer['odoo_user_id']})
                self.cnx.commit()
            STATS_EMAILS['customers_archived'] = str(len(archived_customers))
        except:
            print(traceback.format_exc())

    def get_order_line_category(self, detail_json, key):
        res = json.loads(detail_json)
        category = ''
        total_delivery = 0.0
        for a in res['notesJson']:
            if a['products'][0]['name'] == key:
                if 'catogoryName' in a['products'][0]:
                    category = a['products'][0]['categoryName']
                    total_delivery = res['deliveryMode']['unit']
                    break
                else:
                    category = ''
                    if 'deliveryMode' in res:
                        if res['deliveryMode']:
                            total_delivery = res['deliveryMode']['unit']
                        else:
                            total_delivery = 0.0
                    else:
                        total_delivery = 0.0

        return category, total_delivery

    def get_orders(self):
        order_ids_to_exclude = []

        for order in Order.objects.filter(odoo_order_id__isnull=False):
            order_ids_to_exclude.append(order.odoo_order_id)

        print(str(len(order_ids_to_exclude)))

        # Récupération des commandes
        sql_orders_odoo = "SELECT \
                            so.id as odoo_order_id, \
                            so.partner_id as odoo_user_id, \
                            so.neighborhood_id, \
                            client.email, \
                            commercant.name as supplier_name, \
                            so.supplier_id as odoo_supplier_id, \
                            category_pricelist.name as universe_name, \
                            category_pricelist.id as odoo_universe_id, \
                            so.create_date as order_date, \
                            so.removal_on_site as click_and_collect, \
                            so.amout_total_supplier as basket_amount, \
                            so.montant_livreur_ae as delivery_amount, \
                            so.montant_please as please_amount, \
                            montant_partenariat_concierge as partner_amount, \
                            so.delivery_street as delivery_street, \
                            so.delivery_zip as delivery_zip, \
                            so.delivery_city as delivery_city, \
                            so.rating, \
                            so.rating_comment, \
                            so.state as odoo_order_state, \
                            offre.id as odoo_offer_id, \
                            offre.title as offer_name, \
                            so.voucher_code, \
                            so.montant_coupon, \
                            coupons.name, \
                            so.order_detail_json, \
                            client.dev \
                             \
                        FROM sale_order so \
                        LEFT JOIN website_voucher coupons ON so.gift_voucher_id = coupons.id \
                        JOIN res_partner client ON so.partner_id = client.id  \
                        JOIN res_partner commercant ON so.supplier_id = commercant.id \
                        JOIN neighborhood_neighborhood quartier ON so.neighborhood_id = quartier.id \
                        JOIN product_pricelist offre ON so.pricelist_id = offre.id \
                        JOIN product_type_pricelist pricelist_type ON offre.pricelist_type_id = pricelist_type.id \
                        JOIN product_category_pricelist category_pricelist ON pricelist_type.pricelist_category_id = category_pricelist.id \
                        WHERE so.partner_id IS NOT NULL \
                        AND so.state NOT IN ('draft', 'authorized', 'authorization_progress', 'payment_progress', 'progress', 'cancel', 'litige', 'shipping_except') \
                        AND so.neighborhood_id NOT IN (1,2,10) AND quartier.active IS TRUE \
                        AND so.id NOT IN " + str(tuple(order_ids_to_exclude)) + " ;"

        cur_odoo = self.odoo_cnx.cursor()
        cur_odoo.execute(sql_orders_odoo)
        res_orders = cur_odoo.fetchall()

        lst_orders = []

        for o in res_orders:
            print(o)
            dic_order = {}
            dic_order['odoo_order_id'] = o[0]
            dic_order['odoo_user_id'] = o[1]
            dic_order['neighborhood_id'] = self.get_django_objetc_id('neighborhood', o[2], 'id')
            dic_order['email'] = o[3]
            dic_order['supplier_name'] = str(o[4].replace("'", "\\'"))
            dic_order['odoo_supplier_id'] = o[5]

            if o[5] in SUPPLIERS:
                dic_order['mw_supplier_id'] = SUPPLIERS[o[5]][0]
            else:
                dic_order['mw_supplier_id'] = 'NULL'

            dic_order['universe_name'] = o[6] if o[6] else ''
            dic_order['odoo_universe_id'] = o[7] if o[7] else 'NULL'

            if o[7] in CATEGORIES:
                dic_order['mw_universe_id'] = CATEGORIES[o[7]] if o[7] else 'NULL'
            else:
                dic_order['mw_universe_id'] = 'NULL'

            dic_order['order_date'] = o[8]
            dic_order['click_and_collect'] = o[9]

            dic_order['basket_amount'] = o[10]
            dic_order['delivery_amount'] = o[11] if o[11] else 0
            dic_order['please_amount'] = o[12] if o[12] else 0
            dic_order['partner_amount'] = o[13] if o[12] else 0

            dic_order['delivery_street'] = str(o[14].replace("'", "\\'")) if o[14] else o[14]
            dic_order['delivery_zip'] = o[15] if o[15] else o[15]
            dic_order['delivery_city'] = o[16].replace("'", "\\'") if o[16] else o[16]

            dic_order['rating'] = o[17] if o[17] else 0
            dic_order['comments'] = o[18][:500].replace("'", "\\'") if o[18] else ''

            dic_order['odoo_order_state'] = o[19]
            dic_order['odoo_offer_id'] = o[20]
            if o[21]:
                dic_order['offer_name'] = str(o[21].replace("'", "\\'")) if o[21] else 'NULL'
            else:
                dic_order['offer_name'] = 'NULL'

            dic_order['voucher_code'] = o[22] if o[22] else ''
            dic_order['voucher_amount'] = o[23] if o[23] else 0
            dic_order['voucher_name'] = o[24].replace("'", "''") if o[24] else ''

            dic_order['customer_id'] = self.get_django_objetc_id('customer', o[1], 'id')
            if o[20] in PRICELISTS:
                dic_order['mw_offer_id'] = PRICELISTS[o[20]]
            else:
                dic_order['mw_offer_id'] = 'NULL'

            # Récupération des lignes de la commande
            sql_order_lines_odoo = "SELECT \
                                                            TRIM(name), \
                                                            id, \
                                                            product_uom_qty, \
                                                            subtotal_ttc \
                                                        FROM sale_order_line \
                                                        WHERE order_id = %(order_id)s;" % {'order_id': o[0]}

            cur_odoo_sol = self.odoo_cnx.cursor()
            cur_odoo_sol.execute(sql_order_lines_odoo)
            res_order_lines = cur_odoo_sol.fetchall()

            dic_order['order_lines'] = []
            for l in res_order_lines:
                if o[25]:
                    order_line_json = self.get_order_line_category(o[25], l[0])
                else:
                    order_line_json = ['', 0.00]

                dic_order['order_lines'].append(
                    {'odoo_order_line_id': l[1],
                     'odoo_order_id': o[0],
                     'odoo_user_id': o[1],
                     'label': l[0],
                     'quantity': l[2],
                     'total_amount': l[3]
                     })
            dic_order['total_delivery'] = order_line_json[1]

            lst_orders.append(dic_order)

        return lst_orders

    def update_django_neighborhood(self, neighborhoods):
        sql_query = "SELECT odoo_id, id FROM please_marketing_app_neighborhood WHERE odoo_id = %(odoo_id)s;"
        sql_insert = "INSERT INTO please_marketing_app_neighborhood(name, odoo_id) VALUES('%(name)s', %(odoo_id)s);"

        market_neighborhoods = {}

        for n in neighborhoods:
            cur = self.cnx.cursor()
            cur.execute(sql_query % {'odoo_id': n['odoo_id']})
            res_neigh = cur.fetchall()

            idx = 0
            if not res_neigh:
                r = cur.execute(sql_insert % {'name': n['name'], 'odoo_id': n['odoo_id']})
                self.cnx.commit()
                idx += 1
            else:
                if str(n['odoo_id']) not in market_neighborhoods:
                    market_neighborhoods[str(n['odoo_id'])] = res_neigh[0][1]

        cur.close()
        STATS_EMAILS['neighborhoods'] = str(idx)
        return market_neighborhoods

    def update_customers(self, customers, market_neighborhoods):
        sql_query = "SELECT odoo_user_id, email, neighborhood_id, cb FROM please_marketing_app_customer WHERE odoo_user_id = %(odoo_user_id)s;"
        sql_insert = "INSERT INTO please_marketing_app_customer(first_name, last_name, email, phone, street, zip, city, neighborhood_id, cb, sign_up_date, test_user, signed_up, odoo_user_id) \
                        VALUES('%(first_name)s', \
                        '%(last_name)s', \
                        '%(email)s', \
                        '%(phone)s', \
                        '%(street)s', \
                        '%(zip)s', \
                        '%(city)s', \
                         %(neighborhood_id)s, \
                        '%(cb)s', \
                        '%(sign_up_date)s', \
                         %(test_user)s, \
                         %(signed_up)s, \
                         %(odoo_user_id)s);"
        nb_update = 0
        nb_insert = 0
        for c in customers:
            print(c)
            cur = self.cnx.cursor()
            cur.execute(sql_query % {'odoo_user_id': c['odoo_user_id']})
            res_cust = cur.fetchall()

            if not res_cust:
                nb_insert += 1
                r = cur.execute(
                    sql_insert % {'first_name': '' if not c['first_name'] else c['first_name'].replace("'", "''"),
                                  'last_name': '' if not c['last_name'] else c['last_name'].replace("'", "''"),
                                  'email': c['email'],
                                  'phone': c['phone'],
                                  'street': '' if not c['street'] else c['street'].replace("'", "''"),
                                  'city': '' if not c['city'] else c['city'].replace("'", "''"),
                                  'zip': c['zip'],
                                  'neighborhood_id': market_neighborhoods[str(c['neighborhood'])],
                                  'cb': c['cb'],
                                  'sign_up_date': c['sign_up_date'],
                                  'test_user': c['dev'],
                                  'signed_up': c['signed_up'],
                                  'odoo_user_id': c['odoo_user_id']
                                  })
                self.cnx.commit()

        STATS_EMAILS['customer_added'] = str(nb_insert)
        STATS_EMAILS['customer_updated'] = str(nb_update)

    def insert_orders(self, orders):
        sql_insert = u"INSERT INTO public.please_marketing_app_order(\
                        basket_amount,\
                        click_and_collect,\
                        comments,\
                        delivery_amount,\
                        delivery_city,\
                        delivery_street,\
                        delivery_zip,\
                        email,\
                        neighborhood_id,\
                        odoo_offer_id,\
                        odoo_order_id,\
                        odoo_order_state,\
                        odoo_supplier_id,\
                        odoo_universe_id,\
                        odoo_user_id,\
                        offer_name,\
                        order_date,\
                        partner_amount,\
                        please_amount,\
                        rating,\
                        supplier_name,\
                        universe_name,\
                        voucher_amount,\
                        voucher_code,\
                        voucher_name,\
                        customer_id,\
                        mw_offer_id,\
                        mw_supplier_id\
                        ) \
                        VALUES(%(basket_amount)s,\
                                %(click_and_collect)s,\
                                E'%(comments)s',\
                                %(delivery_amount)s,\
                                E'%(delivery_city)s',\
                                E'%(delivery_street)s',\
                                '%(delivery_zip)s',\
                                '%(email)s',\
                                %(neighborhood_id)s,\
                                %(odoo_offer_id)s,\
                                %(odoo_order_id)s,\
                                '%(odoo_order_state)s',\
                                %(odoo_supplier_id)s,\
                                %(odoo_universe_id)s,\
                                %(odoo_user_id)s,\
                                E'%(offer_name)s',\
                                '%(order_date)s',\
                                %(partner_amount)s,\
                                %(please_amount)s,\
                                %(rating)s,\
                                E'%(supplier_name)s',\
                                E'%(universe_name)s',\
                                %(voucher_amount)s,\
                                '%(voucher_code)s',\
                                '%(voucher_name)s',\
                                %(customer_id)s,\
                                %(mw_offer_id)s,\
                                %(mw_supplier_id)s);"

        cur = self.cnx.cursor()
        i = 0
        for o in orders:
            i += 1
            cur.execute(sql_insert % o)
            self.cnx.commit()
            self.insert_order_lines(cur, o['order_lines'])

        STATS_EMAILS['orders_inserted'] = str(i)

    def insert_order_lines(self, cur, order_lines):
        sql_lines = u"INSERT INTO please_marketing_app_orderline(odoo_order_line_id,\
                            odoo_order_id,\
                            label, quantity,\
                            total_amount,\
                            customer_id,\
                            email,\
                            odoo_user_id)\
                             VALUES(%(odoo_order_line_id)s,\
                                     %(odoo_order_id)s,\
                                     E'%(label)s',\
                                     %(quantity)s,\
                                     %(total_amount)s,\
                                     %(customer_id)s,\
                                     '%(email)s',\
                                     %(odoo_user_id)s);"
        for line in order_lines:
            vals = {'odoo_order_line_id': line['odoo_order_line_id'],
                    'odoo_order_id': line['odoo_order_id'],
                    'label': line['label'].replace("'", "\\'")[:500],
                    'quantity': line['quantity'],
                    'total_amount': line['total_amount'],
                    'customer_id': self.get_django_objetc_id('customer', line['odoo_user_id'], 'id'),
                    'email': self.get_django_objetc_id('customer', line['odoo_user_id'], 'email'),
                    'odoo_user_id': line['odoo_user_id']
                    }
            cur.execute(sql_lines % vals)
            self.cnx.commit()

    def cron_feed_market_db(self):
        STATS_EMAILS['exec_date'] = str(DT.now())
        try:
            print('#### FEED MARKET DB ####')
            # Connexion à la base de données market
            self.connect_to_database()

            # Récupération des données du MW
            self.get_mw_data()

            # Quartiers
            print('### NEIGHBORHOODS ###')
            neighborhoods = self.get_neighborhoods()
            market_neighborhoods = self.update_django_neighborhood(neighborhoods)

            # Clients
            print('### CUSTOMERS ###')
            customers = self.get_customers()
            self.update_customers(customers, market_neighborhoods)

            # Clients désinscrits
            print('### ARCHIVED CUSTOMERS ###')
            archived_customers = self.get_archived_customers()
            self.update_archived_customers(archived_customers)

            # Commandes
            print('### ORDERS ###')
            print('# READ #')
            orders = self.get_orders()
            print('# INSERT #')
            if orders:
                self.insert_orders(orders)

            print('# END #')

            self.disconnect_to_database()
        except:
            print(traceback.format_exc())


def update_sharable_id():

    for customer in Customer.objects.filter(sharable_user_id__isnull=True):
        customer.sharable_user_id = str(uuid.uuid4())
        customer.save()

    return


def import_etl_regular():
    log_script(name="import_etl_regular", status="s")
    try:

        etl = etl_market()
        etl.cron_feed_market_db()
        update_sharable_id()

        log_script(name="import_etl_regular", status="d")

    except:
        print("ERROR: ETL FAILED - " + str(traceback.format_exc()))
