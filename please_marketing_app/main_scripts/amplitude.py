# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, IntercomEvent
from please_marketing_extra_user_enrichment.models import AddressEnrichment
from please_marketing_script_execution.log_script import log_script
import urllib
import requests
from django.conf import settings
import json
import sys
from requests.utils import requote_uri
from concurrent.futures import ThreadPoolExecutor
import datetime


# from please_marketing_app.main_scripts.amplitude import *
def update_amplitude_events(event):
    if event.event_name == "paid order":

        try:

            customer = event.customer

            url = "https://api.amplitude.com/httpapi"

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache',
            }

            json_payload = {

                'event_type': event.event_name,
                'user_id': customer.email,
                'insert_id': str(customer.email + "-" + event.intercom_id),
                'event_id': int(event.id),
                'country': 'France' if not event.geo_country else event.geo_country,
                'ip': '' if not event.ip_address else event.ip_address,
                'app_version': '' if not event.app_version else event.app_version,
                'platform': '' if not event.os_platform else event.os_platform,
                'os_name': '' if not event.os_name else event.os_name,
                'os_version': '' if not event.os_version else event.os_version,
                'device_brand': '' if not event.device_brand else event.device_brand,
                'device_manufacturer': '' if not event.device_manufacturer else event.device_manufacturer,
                'device_model': '' if not event.device_model else event.device_model,
                'carrier': '' if not event.carrier else event.carrier,
                'region': '' if not event.customer.neighborhood.name else event.customer.neighborhood.name,
                'city': '' if not event.geo_city else event.geo_city,
                'dma': '' if not event.customer.neighborhood.name else event.customer.neighborhood.name,
                'language': 'French',
                'location_lat': '' if not event.geo_lat else float(event.geo_lat),
                'location_lng': '' if not event.geo_long else float(event.geo_long),
                'time': '' if not event.created_at else event.created_at.strftime("%s"),
                'price': 0 if not event.basket_amount else float(event.basket_amount),
                'quantity': 1,
                'revenue': 0 if not event.basket_amount else float(event.basket_amount),
                'productId': '' if not event.mw_offer_id else event.mw_offer_id,
                'revenueType': '' if not event.mw_universe_id else event.mw_universe_id,
                'event_properties': {

                    # Core Event Data
                    'channel': 'app' if not event.channel else event.channel,

                    # Event Metadata: checkout
                    'odoo_order_id': '' if not event.odoo_order_id else event.odoo_order_id,
                    'universe_name': '' if not event.universe_name else event.universe_name,
                    'mw_universe_id': '' if not event.mw_universe_id else event.mw_universe_id,
                    'supplier_name': '' if not event.supplier_name else event.supplier_name,
                    'mw_supplier_id': '' if not event.mw_supplier_id else event.mw_supplier_id,
                    'offer_name': '' if not event.offer_name else event.offer_name,
                    'mw_offer_id': '' if not event.mw_offer_id else event.mw_offer_id,
                    'item_name': '' if not event.item_name else event.item_name,
                    'mw_item_id': '' if not event.mw_item_id else event.mw_item_id,
                    'item_list': '' if not event.item_list else event.item_list,
                    'item_number': '' if not event.item_list else int(len(event.item_list)),
                    'voucher_code': '' if not event.voucher_code else event.voucher_code,
                    'voucher_name': '' if not event.voucher_name else event.voucher_name,
                    'voucher_value': '' if not event.voucher_value else float(event.voucher_value),
                    'voucher_type': '' if not event.voucher_type else event.voucher_type,
                    'delivery_amount': '' if not event.delivery_amount else float(event.delivery_amount),
                    'basket_amount': '' if not event.basket_amount else float(event.basket_amount),
                    'please_amount': '' if not event.please_amount else float(event.please_amount),
                    'partner_amount': '' if not event.partner_amount else float(event.partner_amount),
                    'delivery_street': '' if not event.delivery_street else event.delivery_street,
                    'delivery_zip': '' if not event.delivery_zip else event.delivery_zip,
                    'delivery_city': '' if not event.delivery_city else event.delivery_city,
                    'order_date': '' if not event.order_date else event.order_date.isoformat(),
                    'minimum_basket_amount': '' if not event.minimum_basket_amount else float(
                        event.minimum_basket_amount),
                    'rating': '' if not event.rating else int(event.rating),
                    'click_and_collect': '' if not event.click_and_collect else event.click_and_collect,

                    # Event Metadata: general
                    'point_count': '' if not event.point_count else int(event.point_count),
                    'link': '' if not event.link else event.link,
                    'campaign_name': '' if not event.campaign_name else event.campaign_name,
                    'search_term': '' if not event.search_term else event.search_term,
                    'offer_list': '' if not event.offer_list else event.offer_list,
                }
            }

            payload = "api_key=" + str(settings.AMPLITUDE_KEY) + "&event=" + urllib.parse.quote(
                json.dumps(json_payload))

            response = requests.request("POST", url, headers=headers, data=payload)

            event.sent_to_amplitude = True
            event.save()

            print("SUCCESS: New Paid " + str(event.intercom_id) + " event has been saved to Amplitude DB for " + str(
                customer.email))

        except:
            print("ERROR: Event " + str(event.intercom_id) + " hasn't been updated to Amplitude DB - " + str(
                sys.exc_info()))

    else:

        try:

            customer = event.customer

            url = "https://api.amplitude.com/httpapi"

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache',
            }

            json_payload = {

                'event_type': event.event_name,
                'user_id': customer.email,
                'insert_id': str(customer.email + "-" + event.intercom_id),
                'event_id': int(event.id),
                'country': 'France' if not event.geo_country else event.geo_country,
                'ip': '' if not event.ip_address else event.ip_address,
                'app_version': '' if not event.app_version else event.app_version,
                'platform': '' if not event.os_platform else event.os_platform,
                'os_name': '' if not event.os_name else event.os_name,
                'os_version': '' if not event.os_version else event.os_version,
                'device_brand': '' if not event.device_brand else event.device_brand,
                'device_manufacturer': '' if not event.device_manufacturer else event.device_manufacturer,
                'device_model': '' if not event.device_model else event.device_model,
                'carrier': '' if not event.carrier else event.carrier,
                'region': '' if not event.customer.neighborhood.name else event.customer.neighborhood.name,
                'city': '' if not event.geo_city else event.geo_city,
                'dma': '' if not event.customer.neighborhood.name else event.customer.neighborhood.name,
                'language': 'French',
                'location_lat': '' if not event.geo_lat else float(event.geo_lat),
                'location_lng': '' if not event.geo_long else float(event.geo_long),
                'time': '' if not event.created_at else event.created_at.strftime("%s"),
                'event_properties': {

                    # Core Event Data
                    'channel': 'app' if not event.channel else event.channel,

                    # Event Metadata: checkout
                    'odoo_order_id': '' if not event.odoo_order_id else event.odoo_order_id,
                    'universe_name': '' if not event.universe_name else event.universe_name,
                    'mw_universe_id': '' if not event.mw_universe_id else event.mw_universe_id,
                    'supplier_name': '' if not event.supplier_name else event.supplier_name,
                    'mw_supplier_id': '' if not event.mw_supplier_id else event.mw_supplier_id,
                    'offer_name': '' if not event.offer_name else event.offer_name,
                    'mw_offer_id': '' if not event.mw_offer_id else event.mw_offer_id,
                    'item_name': '' if not event.item_name else event.item_name,
                    'mw_item_id': '' if not event.mw_item_id else event.mw_item_id,
                    'item_list': '' if not event.item_list else event.item_list,
                    'item_number': '' if not event.item_list else int(len(event.item_list)),
                    'voucher_code': '' if not event.voucher_code else event.voucher_code,
                    'voucher_name': '' if not event.voucher_name else event.voucher_name,
                    'voucher_value': '' if not event.voucher_value else float(event.voucher_value),
                    'voucher_type': '' if not event.voucher_type else event.voucher_type,
                    'delivery_amount': '' if not event.delivery_amount else float(event.delivery_amount),
                    'basket_amount': '' if not event.basket_amount else float(event.basket_amount),
                    'please_amount': '' if not event.please_amount else float(event.please_amount),
                    'partner_amount': '' if not event.partner_amount else float(event.partner_amount),
                    'delivery_street': '' if not event.delivery_street else event.delivery_street,
                    'delivery_zip': '' if not event.delivery_zip else event.delivery_zip,
                    'delivery_city': '' if not event.delivery_city else event.delivery_city,
                    'order_date': '' if not event.order_date else event.order_date.isoformat(),
                    'minimum_basket_amount': '' if not event.minimum_basket_amount else float(
                        event.minimum_basket_amount),
                    'rating': '' if not event.rating else int(event.rating),
                    'click_and_collect': '' if not event.click_and_collect else event.click_and_collect,

                    # Event Metadata: general
                    'point_count': '' if not event.point_count else int(event.point_count),
                    'link': '' if not event.link else event.link,
                    'campaign_name': '' if not event.campaign_name else event.campaign_name,
                    'search_term': '' if not event.search_term else event.search_term,
                    'offer_list': '' if not event.offer_list else event.offer_list,
                }
            }

            payload = "api_key=" + str(settings.AMPLITUDE_KEY) + "&event=" + urllib.parse.quote(
                json.dumps(json_payload))
            #

            response = requests.request("POST", url, headers=headers, data=payload)

            event.sent_to_amplitude = True
            event.save()

            print("SUCCESS: New " + str(event.intercom_id) + " event has been saved to Amplitude DB for " + str(
                customer.email))

        except:
            print("ERROR: Event " + str(event.intercom_id) + " hasn't been updated to Amplitude DB - " + str(
                sys.exc_info()))

    return


# from please_marketing_app.main_scripts.amplitude import *
def executor_update_amplitude_events():
    log_script(name="executor_update_amplitude_events", status="s")
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(update_amplitude_events, IntercomEvent.objects.filter(sent_to_amplitude=False, updated_ip=True, customer__test_user=False))
    log_script(name="executor_update_amplitude_events", status="d")
    return


def update_amplitude_users(customer):
    try:

        url = "https://api.amplitude.com/httpapi"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
        }

        json_payload = {
            'event_type': '$identify',
            'user_id': customer.email,
            'country': 'France',
            'ip': '' if not customer.last_seen_ip else customer.last_seen_ip,
            'app_version': '' if not customer.app_version else customer.app_version,
            'platform': '' if not customer.os_platform else customer.os_platform,
            'os_name': '' if not customer.os_name else customer.os_name,
            'os_version': '' if not customer.os_version else customer.os_version,
            'device_brand': '' if not customer.device_brand else customer.device_brand,
            'device_manufacturer': '' if not customer.device_manufacturer else customer.device_manufacturer,
            'device_model': '' if not customer.device_model else customer.device_model,
            'carrier': '' if not customer.carrier else customer.carrier,
            'region': '' if not customer.neighborhood.name else customer.neighborhood.name,
            'city': '' if not customer.city else customer.city,
            'dma': '' if not customer.neighborhood.name else customer.neighborhood.name,
            'language': 'French',
            'location_lat': '' if not customer.w_latitude else float(customer.w_latitude),
            'location_lng': '' if not customer.w_longitude else float(customer.w_longitude),
            'time': '' if not customer.sign_up_date else customer.sign_up_date.strftime("%s"),
            'user_properties': {
                '$set': {

                    # Personal Info
                    'signed_up': 'true' if not customer.signed_up else customer.signed_up,
                    'first_name': customer.first_name.capitalize(),
                    'last_name': customer.last_name.capitalize(),
                    'gender': '' if not customer.gender else customer.gender,
                    'age': '' if not customer.age else customer.age,
                    'email': customer.email,
                    'phone': str(customer.phone),
                    'street': '' if not customer.street else customer.street,
                    'zip': '' if not customer.zip else customer.zip,
                    'city': '' if not customer.city else customer.city,
                    'neighborhood': '' if not customer.neighborhood.name else customer.neighborhood.name,
                    'cb': '' if not customer.cb else customer.cb,
                    'sign_up_date': '' if not customer.sign_up_date else customer.sign_up_date.isoformat(),
                    'profile_picture': '' if not customer.profile_picture else customer.profile_picture,

                    # Family Info
                    'family': 'false' if not customer.family else customer.family,

                    # Order Info
                    'orders_number': int(0) if not customer.orders_number else int(customer.orders_number),
                    'total_spent': float(0) if not customer.total_spent else float(customer.total_spent),
                    'total_voucher': float(0) if not customer.total_voucher else float(customer.total_voucher),
                    'average_basket': float(0) if not customer.average_basket else float(customer.average_basket),
                    'average_rating': float(0) if not customer.average_rating else float(customer.average_rating),
                    'last_order_date': '' if not customer.last_order_date else customer.last_order_date.isoformat(),

                    # Retention Info
                    'unsubscribed_from_emails': 'false' if not customer.unsubscribed_from_emails else customer.unsubscribed_from_emails,
                    'last_request_at': '' if not customer.last_request_at else customer.last_request_at.isoformat(),
                    'session_count': int(0) if not customer.session_count else int(customer.session_count),

                    # Other Info
                    'counter_reset_password': int(0) if not customer.counter_reset_password else int(
                        customer.counter_reset_password),

                    # Referral Info
                    'referral_leads_counter': int(0) if not customer.referral_leads_counter else int(
                        customer.referral_leads_counter),
                    'referral_counter': int(0) if not customer.referral_counter else int(
                        customer.referral_counter),
                }
            }
        }

        payload = "api_key=" + str(settings.AMPLITUDE_KEY) + "&event=" + urllib.parse.quote(json.dumps(json_payload))

        response = requests.request("POST", url, headers=headers, data=payload)

        print("SUCCESS: User " + str(customer.email) + " has been updated to Amplitude DB")

    except:
        print("ERROR: User " + str(customer.email) + " hasn't been updated to Amplitude DB - " + str(
            sys.exc_info()))

    return


# from please_marketing_app.main_scripts.amplitude import *
def executor_update_amplitude_users():
    log_script(name="executor_update_amplitude_users", status="s")

    with ThreadPoolExecutor(max_workers=4) as executor:
        inclusion_list = list(
            IntercomEvent.objects.filter(
                neighborhood__isnull=False,
                customer__isnull=False,
                customer__email__isnull=False,
                customer__test_user=False,
                created_at__gt=datetime.datetime.fromtimestamp(
                    float((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))
            ).distinct("customer__id").values_list("customer__id", flat=True)
        )

        executor.map(update_amplitude_users, Customer.objects.filter(id__in=inclusion_list))
    log_script(name="executor_update_amplitude_users", status="d")
    return
