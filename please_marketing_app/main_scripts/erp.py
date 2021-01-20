# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, OrderLine, IntercomEvent
import requests
import datetime
import sys
from django.conf import settings
import urllib
from django.db.models import Avg, Sum
import json
import time
from please_marketing_script_execution.log_script import log_script
from concurrent.futures import ThreadPoolExecutor


# from please_marketing_app.main_scripts.erp import *
# UPDATE ORDER CALCULATED FIELDS
def update_paid_amount(order):
    order.paid_amount = order.basket_amount - order.voucher_amount
    order.save()
    return


def executor_update_paid_amount():
    log_script(name="executor_update_paid_amount", status="s")

    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(update_paid_amount, Order.objects.filter(basket_amount__isnull=False, paid_amount__isnull=True, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%s")))))

    log_script(name="executor_update_paid_amount", status="d")
    return


# UPDATE MARKETING AND ARCHIVED FIELD
def update_marketing_archived():
    log_script(name="update_marketing_archived", status="s")
    Customer.objects.filter(marketing=None).update(marketing=True)
    Customer.objects.filter(archived=None).update(archived=False)
    log_script(name="update_marketing_archived", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
# UPDATE OF USER'S INFORMATION
def update_gender():
    log_script(name="update_gender", status="s")

    for fname in Customer.objects.filter(gender__isnull=True):
        print("Current first name working on is: " + str(fname.first_name))

        if Customer.objects.filter(first_name=fname.first_name, gender__isnull=False).count() > 0:

            target = Customer.objects.filter(first_name=fname.first_name, gender__isnull=False).first()

            Customer.objects.filter(first_name=fname.first_name, gender__isnull=True).update(
                gender=str(target.gender))

            print("SUCCESS: Updated Gender Status for first name (DB) " + str(fname.first_name) + " - Count: " + str(
                Customer.objects.filter(first_name=fname.first_name).count()))

        elif Customer.objects.filter(first_name=fname.first_name, gender__isnull=True).count() > 0:

            try:
                url = "https://gender-api.com/get"

                querystring = {
                    "name": fname.first_name,
                    "key": str(settings.GENDER_KEY)
                }

                headers = {
                    'cache-control': "no-cache"
                }

                response = requests.request("GET", url, headers=headers, params=querystring).json()

                if int(response.get("accuracy")) >= 60:

                    Customer.objects.filter(first_name=fname.first_name, gender__isnull=True).update(gender=str(response.get("gender")))

                    print("SUCCESS: Updated Gender Status for first name (API) " + str(fname.first_name) + " - Count: " + str(Customer.objects.filter(first_name=fname.first_name).count()))

                elif response.get("errno") == 30:
                    print("WARNING: Gender API Rate Limit Reached !")

                elif int(response.get("accuracy")) < 60:
                    Customer.objects.filter(first_name=fname.first_name, gender__isnull=True).update(gender="unknown")
                    print("WARNING: Updated to Unknown Gender Status (low accuracy) for first name (API) " + str(fname.first_name) + " - Count: " + str(Customer.objects.filter(first_name=fname.first_name).count()))

                else:
                    Customer.objects.filter(first_name=fname.first_name, gender__isnull=True).update(gender="unknown")
                    print("WARNING: Updated to Unknown Gender Status for first name (API) " + str(fname.first_name) + " - Count: " + str(Customer.objects.filter(first_name=fname.first_name).count()))

            except:
                print("ERROR: Not Updated Gender Status for user " + str(fname.first_name) + " - " + str(sys.exc_info()))

    log_script(name="update_gender", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_address():
    log_script(name="update_address", status="s")

    for customer in Customer.objects.filter(city__isnull=False, street__isnull=False, zip__isnull=False,
                                            w_latitude__isnull=True, w_longitude__isnull=True):
        try:
            address = str(customer.street + " " + customer.city + " " + customer.zip).replace(" ", "+")
            url = str(
                "https://maps.googleapis.com/maps/api/geocode/json?address="
                + address
                + "&key="
                + str(settings.GOOGLE_GEOCODING_KEY)
            )

            response = requests.request("GET", url).json()

            if response.get("status") == "OK":
                location = response.get("results")[0].get("geometry").get("location")

                customer.w_longitude = location.get("lng")
                customer.w_latitude = location.get("lat")
                customer.save()
                print("SUCCESS: " + str(customer.email) + " Google API has recognised the address" + " - Raw Data: "
                      + str(customer.street + ", " + customer.city + ", " + customer.zip))

            else:
                print(
                        "ERROR: Google API hasn't recognised the address for user "
                        + str(customer.email)
                        + " - Raw Data: "
                        + str(customer.street + ", " + customer.city + ", " + customer.zip)
                )

        except:
            customer.w_longitude = None
            customer.w_latitude = None
            customer.save()
            print("ERROR: Google API hasn't recognised the address for user " + str(customer.email) + " - " + str(sys.exc_info()) + " - Raw Data: "
                  + str(customer.street + ", " + customer.city + ", " + customer.zip))

    log_script(name="update_address", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_counter_password():
    log_script(name="update_counter_password", status="s")

    # Updating how many times a user used Reset Password
    for cus_id in IntercomEvent.objects.filter(event_name__iexact="clicked reset password", customer__isnull=False, created_at__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))).values("customer").distinct():
        customer = Customer.objects.get(id=cus_id.get("customer"))

        try:
            counter = IntercomEvent.objects.filter(event_name__iexact="clicked reset password",
                                                   customer=customer).count()
            customer.counter_reset_password = counter
            customer.save()
            print("SUCCESS: Updated reset password counter to " + str(counter) + " to user " + str(customer.email))

        except:
            print("ERROR: Failed to update reset password counter to user " + str(customer.email) + " - " + str(
                sys.exc_info()))

    log_script(name="update_counter_password", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_user_device():
    log_script(name="update_user_device", status="s")

    # Updating user device based on latest IntercomEvent
    for cus_id in IntercomEvent.objects.filter(
            customer__device_brand__isnull=True,
            customer__isnull=False,
            created_at__gt=datetime.datetime.fromtimestamp(
                float((datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%s")))
    ).values("customer").distinct():

        try:
            customer = Customer.objects.get(id=cus_id.get("customer"))
            lt_event = IntercomEvent.objects.filter(customer=customer).order_by("-created_date").first()

            customer.device_brand = None if not lt_event.device_brand else lt_event.device_brand
            customer.device_model = None if not lt_event.device_model else lt_event.device_model
            customer.device_manufacturer = None if not lt_event.device_manufacturer else lt_event.device_manufacturer
            customer.os_name = None if not lt_event.os_name else lt_event.os_name
            customer.os_platform = None if not lt_event.os_platform else lt_event.os_platform
            customer.os_version = None if not lt_event.os_version else lt_event.os_version
            customer.app_version = None if not lt_event.app_version else lt_event.app_version
            customer.carrier = None if not lt_event.carrier else lt_event.carrier
            customer.last_seen_ip = None if not lt_event.ip_address else lt_event.ip_address

            customer.save()
            print("SUCCESS: Updated user device for user " + str(customer.email))

        except:
            print("ERROR: Failed to update user device for user " + str(cus_id) + " - " + str(
                sys.exc_info()))

    log_script(name="update_user_device", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_user_device_30():
    log_script(name="update_user_device_30", status="s")

    # Updating user device based on latest IntercomEvent
    for cus_id in IntercomEvent.objects.filter(
            customer__isnull=False,
            created_at__gt=datetime.datetime.fromtimestamp(
                float((datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%s")))
    ).values("customer").distinct():

        try:
            customer = Customer.objects.get(id=cus_id.get("customer"))
            lt_event = IntercomEvent.objects.filter(customer=customer).order_by("-created_date").first()

            if (customer.device_brand != lt_event.device_brand) or (customer.os_version !=lt_event.os_version):

                customer.device_brand = None if not lt_event.device_brand else lt_event.device_brand
                customer.device_model = None if not lt_event.device_model else lt_event.device_model
                customer.device_manufacturer = None if not lt_event.device_manufacturer else lt_event.device_manufacturer
                customer.os_name = None if not lt_event.os_name else lt_event.os_name
                customer.os_platform = None if not lt_event.os_platform else lt_event.os_platform
                customer.os_version = None if not lt_event.os_version else lt_event.os_version
                customer.app_version = None if not lt_event.app_version else lt_event.app_version
                customer.carrier = None if not lt_event.carrier else lt_event.carrier
                customer.last_seen_ip = None if not lt_event.ip_address else lt_event.ip_address

                customer.save()
                print("SUCCESS: Updated user device 30 for user " + str(customer.email))

        except:
            print("ERROR: Failed to update user device 30 for user " + str(cus_id) + " - " + str(
                sys.exc_info()))

    log_script(name="update_user_device_30", status="d")
    return


# UPDATE OF USER'S ORDERS INFORMATION
# from please_marketing_app.main_scripts.erp import *
def update_last_order_date():
    log_script(name="update_last_order_date", status="s")

    for cus_id in Order.objects.filter(odoo_order_state="done", customer__isnull=False, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%s")))).values("customer").distinct():

        try:

            customer = Customer.objects.get(id=cus_id.get("customer"))

            last_order = Order.objects.filter(customer=customer, odoo_order_state="done").order_by("-order_date").first()
            customer.last_order_date = last_order.order_date
            customer.save()

            print("SUCCESS: Updated Last Order Date to Please Market DB for user " + str(customer.email))

        except:
            print("ERROR: Not Updated Last Order Date for user " + str(cus_id) + " - " + str(sys.exc_info()))

    log_script(name="update_last_order_date", status="d")
    return


def update_average_mark():
    log_script(name="update_average_mark", status="s")

    for cus_id in Order.objects.filter(odoo_order_state="done", customer__isnull=False, rating__isnull=False, rating__gt=0, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%s")))).values("customer").distinct():

        customer = Customer.objects.get(id=cus_id.get("customer"))
        customer.average_rating = Order.objects.filter(customer=customer, odoo_order_state="done", rating__isnull=False, rating__gt=0).aggregate(Avg("rating")).get("rating__avg")
        customer.save()
        print("SUCCESS: Updated Average Mark (" + str(customer.average_rating) + ") to Please Market DB for user " + str(customer.email))

    log_script(name="update_average_mark", status="d")
    return


def update_average_basket():
    log_script(name="update_average_basket", status="s")

    for cus_id in Order.objects.filter(odoo_order_state="done", customer__isnull=False, basket_amount__isnull=False, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%s")))).values("customer").distinct():

        customer = Customer.objects.get(id=cus_id.get("customer"))
        customer.average_basket = Order.objects.filter(customer=customer, odoo_order_state="done", basket_amount__isnull=False).aggregate(Avg("basket_amount")).get("basket_amount__avg")
        customer.save()
        print("SUCCESS: Updated Average Basket (" + str(customer.average_basket) + " €) to Please Market DB for user " + str(customer.email))

    log_script(name="update_average_basket", status="d")
    return


def update_orders_number():
    log_script(name="update_orders_number", status="s")

    for cus_id in Order.objects.filter(odoo_order_state="done", customer__isnull=False, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%s")))).values("customer").distinct():

        customer = Customer.objects.get(id=cus_id.get("customer"))
        customer.orders_number = Order.objects.filter(customer=customer, odoo_order_state="done").count()
        customer.save()
        print("SUCCESS: Updated Orders Number to (" + str(customer.orders_number) + ") to Please Market DB for user " + str(customer.email))

    log_script(name="update_orders_number", status="d")
    return


def update_total_spent():
    log_script(name="update_total_spent", status="s")

    for cus_id in Order.objects.filter(odoo_order_state="done", customer__isnull=False, basket_amount__isnull=False, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%s")))).values("customer").distinct():

        customer = Customer.objects.get(id=cus_id.get("customer"))
        customer.total_spent = Order.objects.filter(customer=customer, odoo_order_state="done", basket_amount__isnull=False).aggregate(Sum("basket_amount")).get("basket_amount__sum")
        customer.save()
        print("SUCCESS: Updated Total Spent to (" + str(customer.total_spent) + " €) to Please Market DB for user " + str(customer.email))

    log_script(name="update_total_spent", status="d")
    return


def update_total_voucher():
    log_script(name="update_total_voucher", status="s")

    for cus_id in Order.objects.filter(odoo_order_state="done", customer__isnull=False, voucher_amount__isnull=False, order_date__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=10)).strftime("%s")))).values("customer").distinct():

        customer = Customer.objects.get(id=cus_id.get("customer"))
        customer.total_voucher = Order.objects.filter(customer=customer, odoo_order_state="done", voucher_amount__isnull=False).aggregate(Sum("voucher_amount")).get("voucher_amount__sum")
        customer.save()
        print("SUCCESS: Updated Total Voucher to (" + str(customer.total_voucher) + " €) to Please Market DB for user " + str(customer.email))

    log_script(name="update_total_voucher", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_no_orders_done():
    log_script(name="update_no_orders_done", status="s")

    exclusion_list = list(
        Order.objects.filter(odoo_order_state="done", customer__isnull=False).distinct("customer__id").values_list(
            "customer__id", flat=True)
    )

    Customer.objects.filter(odoo_user_id__isnull=False).exclude(id__in=exclusion_list).update(
        total_spent=0,
        orders_number=0,
        total_voucher=0,
        average_basket=None,
        average_rating=None
    )

    print("SUCCESS: Updated NO ORDERS DONE to 0 to Please Market DB")

    log_script(name="update_no_orders_done", status="d")
    return


def update_paid_order_events():
    log_script(name="update_paid_order_events", status="s")

    for event in IntercomEvent.objects.filter(event_name="paid order", odoo_order_id__isnull=False, created_at__gt=datetime.datetime.fromtimestamp(float((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))):

        if Order.objects.filter(odoo_order_id=event.odoo_order_id, odoo_order_state="done", customer__test_user=False).count() == 1:

            try:

                target_order = Order.objects.get(odoo_order_id=event.odoo_order_id, odoo_order_state="done")

                event.click_and_collect = target_order.click_and_collect

                event.basket_amount = target_order.basket_amount
                event.please_amount = target_order.please_amount
                event.delivery_amount = target_order.delivery_amount
                event.partner_amount = target_order.partner_amount

                event.voucher_code = target_order.voucher_code
                event.voucher_name = target_order.voucher_name
                event.voucher_value = target_order.voucher_amount

                event.rating = target_order.rating

                event.delivery_street = target_order.delivery_street
                event.delivery_city = target_order.delivery_city
                event.delivery_zip = target_order.delivery_zip

                event.mw_universe_id = target_order.mw_universe_id
                event.universe_name = target_order.universe_name
                event.mw_offer_id = target_order.mw_offer_id
                event.offer_name = target_order.offer_name
                event.mw_supplier_id = target_order.mw_supplier_id
                event.supplier_name = target_order.supplier_name

                event.save()

                print("SUCCESS: Updated paid orders event to Please Market DB for user " + str(event.customer.email))

            except:
                print("ERROR: Not Updated paid orders event to Please Market DB for user " + str(event.customer.email) + " - " + str(sys.exc_info()))

        elif Order.objects.filter(odoo_order_id=event.odoo_order_id, odoo_order_state="done", customer__test_user=False).count() > 1:
            print("WARNING: Multiple orders found for updating event " + event.intercom_id + " to Please Market DB for user " + str(event.customer.email))

        elif Order.objects.filter(odoo_order_id=event.odoo_order_id, odoo_order_state="done", customer__test_user=False).count() == 0:
            print("WARNING: No order found for updating event " + event.intercom_id + " to Please Market DB for user " + str(event.customer.email))

    log_script(name="update_paid_order_events", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_intercom_events_ip(ip):

    # Updating the IP Location of an event
    try:
        url = str("https://api.ipdata.co/" + str(ip.get("ip_address")) + "?api-key=" + settings.IP_API_KEY)
        response = requests.request("GET", url).json()

        url_carrier = str("https://api.ipdata.co/" + str(ip.get("ip_address")) + "/carrier?api-key=" + settings.IP_API_KEY)
        response_carrier = requests.request("GET", url_carrier).json()

        geo_country = None if not response else response.get("country_name")
        geo_city = None if not response else response.get("city")
        geo_zip_code = None if not response else response.get("postal")
        geo_lat = None if not response else response.get("latitude")
        geo_long = None if not response else response.get("longitude")
        carrier = None if not response_carrier else response_carrier.get("name")

        IntercomEvent.objects.filter(updated_ip=None, ip_address=ip.get("ip_address")).update(
            geo_country=geo_country,
            geo_city=geo_city,
            geo_zip_code=geo_zip_code,
            geo_lat=geo_lat,
            geo_long=geo_long,
            carrier=carrier,
            updated_ip=True,
        )

        print("SUCCESS: IP Addresses decoded from API for all its related Events - " + str(ip.get("ip_address")))

    except:
        print("ERROR: IP Addresses NOT decoded from API for all its related Events - " + str(ip.get("ip_address")) + " - error " + str(sys.exc_info()))

    return


# from please_marketing_app.main_scripts.erp import *
def executor_update_intercom_events_ip():
    log_script(name="executor_update_intercom_events_ip", status="s")

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(
            update_intercom_events_ip,
            IntercomEvent.objects.filter(
                updated_ip=None,
                created_at__gt=datetime.datetime.fromtimestamp(
                float((datetime.datetime.today() - datetime.timedelta(days=4)).strftime("%s")))).values("ip_address").distinct()
        )

    log_script(name="executor_update_intercom_events_ip", status="d")
    return


# from please_marketing_app.main_scripts.erp import *
def update_intercom_events_neighborhood():
    log_script(name="update_intercom_events_neighborhood", status="s")

    # Updating the Neighborhood of where an event occurred
    for customer in IntercomEvent.objects.filter(
            neighborhood__isnull=True,
            customer__isnull=False,
            customer__neighborhood__isnull=False,
            customer__odoo_user_id__isnull=False,
            created_at__gt=datetime.datetime.fromtimestamp(
                float((datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%s")))
    ).values("customer").distinct():

        try:

            target_customer = Customer.objects.get(id=customer.get("customer"))

            IntercomEvent.objects.filter(customer=target_customer, neighborhood__isnull=True).update(
                neighborhood=target_customer.neighborhood
            )

            print("SUCCESS: Added Neighborhood (from customer) to Intercom Events for user - " + str(target_customer.email))

        except:
            print("ERROR: for user " + str(customer) + " - error " + str(sys.exc_info()))

    log_script(name="update_intercom_events_neighborhood", status="d")
    return
