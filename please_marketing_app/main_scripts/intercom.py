# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, IntercomEvent, Neighborhood
from please_marketing_extra_user_enrichment.models import AddressEnrichment
import requests
import datetime
from pytz import timezone
import sys
from django.conf import settings
import json
from concurrent.futures import ThreadPoolExecutor
from please_marketing_script_execution.log_script import log_script
from please_marketing_app.main_scripts.retrieve_vb1_data import retrieve_vb1


# from please_marketing_app.main_scripts.intercom import *
def save_intercom_events_30(customer):
    try:
        next_page = str("https://api.intercom.io/events?type=user&email="
                        + customer.email
                        + "&since=" + str((datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%s")))

        while next_page is not None:
            url = next_page
            headers = {
                "Authorization": str(settings.INTERCOM_KEY),
                "Accept": "application/json"
            }

            response = requests.request("GET", url, headers=headers).json()

            if (response.get("type") == "event.list") and (len(response.get("events")) > 0):

                for event in response.get("events"):
                    event_raw = IntercomEvent.objects.filter(intercom_id=event.get("id"))
                    event_number = event_raw.count()

                    if event_number == 0:

                        try:
                            item_list = event.get("metadata").get("item_list").split(";")
                        except AttributeError:
                            item_list = []

                        try:
                            offer_list = event.get("metadata").get("offer_list").split(";")
                        except AttributeError:
                            offer_list = []

                        try:
                            universe_name = event.get("metadata").get("universe_name").lower().replace("_", " ")
                            universe_id = event.get("metadata").get("mw_universe_id")
                        except AttributeError:
                            universe_name = None
                            universe_id = None

                        try:
                            offer_name = event.get("metadata").get("offer_name").lower().replace("_", " ")
                            offer_id = event.get("metadata").get("mw_offer_id")
                        except AttributeError:
                            offer_name = None
                            offer_id = None

                        try:
                            supplier_name = event.get("metadata").get("supplier_name").lower().replace("_", " ")
                            supplier_id = event.get("metadata").get("mw_supplier_id")
                        except AttributeError:
                            supplier_name = None
                            supplier_id = None

                        try:
                            item_name = event.get("metadata").get("item_name").lower().replace("_", " ")
                            item_id = event.get("metadata").get("mw_item_id")
                        except AttributeError:
                            item_name = None
                            item_id = None

                        IntercomEvent(
                            customer=customer,
                            neighborhood=customer.neighborhood,
                            event_name=event.get("event_name"),
                            created_at=datetime.datetime.fromtimestamp(float(event.get("created_at")),
                                                                       timezone('Europe/Paris')),
                            user_id=customer.email,
                            intercom_user_id=event.get("intercom_user_id"),
                            intercom_id=event.get("id"),
                            channel="app" if not event.get("metadata").get("from") else event.get("metadata").get("from"),
                            app_version=event.get("metadata").get("app_version"),
                            os_platform=event.get("metadata").get("os_name"),
                            os_name=event.get("metadata").get("os_name"),
                            os_version=event.get("metadata").get("os_version"),
                            device_brand=event.get("metadata").get("device_brand"),
                            device_model=event.get("metadata").get("device_model"),
                            device_manufacturer=event.get("metadata").get("device_brand"),
                            user_agent_data=event.get("metadata").get("user_agent_data"),
                            carrier=event.get("metadata").get("carrier"),
                            ip_address=event.get("metadata").get("ip_address"),
                            referer_domain=event.get("metadata").get("referer_domain"),
                            universe_name=universe_name,
                            mw_universe_id=universe_id,
                            supplier_name=supplier_name,
                            mw_supplier_id=supplier_id,
                            offer_name=offer_name,
                            mw_offer_id=offer_id,
                            item_name=item_name,
                            mw_item_id=item_id,
                            item_list=item_list,
                            offer_list=offer_list,
                            search_term=event.get("metadata").get("search_term"),
                            voucher_code=event.get("metadata").get("voucher_code"),
                            voucher_name=event.get("metadata").get("voucher_name"),
                            voucher_value=event.get("metadata").get("voucher_value"),
                            voucher_type=event.get("metadata").get("voucher_type"),
                            basket_amount=event.get("metadata").get("basket_amount"),
                            delivery_amount=event.get("metadata").get("delivery_amount"),
                            please_amount=event.get("metadata").get("please_amount"),
                            partner_amount=event.get("metadata").get("partner_amount"),
                            minimum_basket_amount=event.get("metadata").get("minimum_basket_amount"),
                            delivery_street=event.get("metadata").get("delivery_street"),
                            delivery_zip=event.get("metadata").get("delivery_zip"),
                            delivery_city=event.get("metadata").get("delivery_city"),
                            order_date=event.get("metadata").get("order_date"),
                            odoo_order_id=event.get("metadata").get("order_id"),
                            point_count=event.get("metadata").get("point_count"),
                            link=event.get("metadata").get("link"),
                            campaign_name=event.get("metadata").get("campaign_name"),
                            sent_to_amplitude=False
                        ).save()

                        print("SUCCESS: New " + str(
                            event.get("id")) + " event has been saved to Please Market DB for " + str(customer.email))

                    elif event_number == 1:

                        print("SUCCESS: " + str(
                            event.get("id")) + " event has already been added to Please Market DB for " + str(
                            customer.email))

                    else:
                        print("WARNING: Probably an issue or duplicated events for user " + str(customer.email))

            elif (response.get("type") == "event.list") and (len(response.get("events")) == 0):
                print("WARNING: No event found on Intercom DB for user " + str(customer.email))

            else:
                print("WARNING: Unknown issue for user " + str(customer.email))

            try:
                next_page = response.get("pages").get("next")
                print("Next Page is: " + str(next_page))
            except AttributeError:
                next_page = None
                print("Next Page is: " + str(next_page))
    except:
        print("ERROR: " + str(customer) + " events 30 hasn't been saved to Please Market DB - " + str(sys.exc_info()))
    return


def executor_save_intercom_events_30():
    log_script(name="executor_save_intercom_events_30", status="s")

    with ThreadPoolExecutor(max_workers=8) as executor:
        # inclusion_list = list(
        #     IntercomEvent.objects.filter(
        #         neighborhood__isnull=False,
        #         customer__isnull=False,
        #         customer__email__isnull=False,
        #         created_at__gt=datetime.datetime.fromtimestamp(
        #             float((datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%s")))
        #     ).distinct("customer__id").values_list("customer__id", flat=True)
        # )

        executor.map(
            save_intercom_events_30,
            Customer.objects.filter(
                sign_up_date__gt=datetime.datetime.fromtimestamp(
                    float((datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%s"))
                )
            )
        )

    log_script(name="executor_save_intercom_events_30", status="d")
    return


# from please_marketing_app.main_scripts.intercom import *
def executor_save_intercom_events_recover():
    log_script(name="executor_save_intercom_events_recover", status="s")

    with ThreadPoolExecutor(max_workers=8) as executor:
        # inclusion_list = list(
        #     IntercomEvent.objects.filter(
        #         neighborhood__isnull=False,
        #         customer__isnull=False,
        #         customer__email__isnull=False,
        #         created_at__gt=datetime.datetime.fromtimestamp(
        #             float((datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%s")))
        #     ).distinct("customer__id").values_list("customer__id", flat=True)
        # )

        executor.map(
            save_intercom_events_30,
            Customer.objects.filter(
                sign_up_date__gt=datetime.datetime.fromtimestamp(
                    float((datetime.datetime.today() - datetime.timedelta(days=16)).strftime("%s"))
                ),
                sign_up_date__lt=datetime.datetime.fromtimestamp(
                    float((datetime.datetime.today() - datetime.timedelta(days=9)).strftime("%s"))
                )
            )
        )

    log_script(name="executor_save_intercom_events_recover", status="d")
    return


def save_intercom_events_2(customer):
    try:
        print("Current user working on is: " + str(customer.email))
        next_page = str("https://api.intercom.io/events?type=user&email="
                        + customer.email
                        + "&since=" + str((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))

        while next_page is not None:
            url = next_page
            headers = {
                "Authorization": str(settings.INTERCOM_KEY),
                "Accept": "application/json"
            }

            response = requests.request("GET", url, headers=headers).json()

            if (response.get("type") == "event.list") and (len(response.get("events")) > 0):

                for event in response.get("events"):
                    event_raw = IntercomEvent.objects.filter(intercom_id=event.get("id"))
                    event_number = event_raw.count()

                    if event_number == 0:

                        try:
                            item_list = event.get("metadata").get("item_list").split(";")
                        except AttributeError:
                            item_list = []

                        try:
                            offer_list = event.get("metadata").get("offer_list").split(";")
                        except AttributeError:
                            offer_list = []

                        try:
                            universe_name = event.get("metadata").get("universe_name").lower().replace("_", " ")
                            universe_id = event.get("metadata").get("mw_universe_id")
                        except AttributeError:
                            universe_name = None
                            universe_id = None

                        try:
                            offer_name = event.get("metadata").get("offer_name").lower().replace("_", " ")
                            offer_id = event.get("metadata").get("mw_offer_id")
                        except AttributeError:
                            offer_name = None
                            offer_id = None

                        try:
                            supplier_name = event.get("metadata").get("supplier_name").lower().replace("_", " ")
                            supplier_id = event.get("metadata").get("mw_supplier_id")
                        except AttributeError:
                            supplier_name = None
                            supplier_id = None

                        try:
                            item_name = event.get("metadata").get("item_name").lower().replace("_", " ")
                            item_id = event.get("metadata").get("mw_item_id")
                        except AttributeError:
                            item_name = None
                            item_id = None

                        IntercomEvent(
                            customer=customer,
                            neighborhood=customer.neighborhood,
                            event_name=event.get("event_name"),
                            created_at=datetime.datetime.fromtimestamp(float(event.get("created_at")),
                                                                       timezone('Europe/Paris')),
                            user_id=customer.email,
                            intercom_user_id=event.get("intercom_user_id"),
                            intercom_id=event.get("id"),
                            channel="app" if not event.get("metadata").get("from") else event.get("metadata").get("from"),
                            app_version=event.get("metadata").get("app_version"),
                            os_platform=event.get("metadata").get("os_name"),
                            os_name=event.get("metadata").get("os_name"),
                            os_version=event.get("metadata").get("os_version"),
                            device_brand=event.get("metadata").get("device_brand"),
                            device_model=event.get("metadata").get("device_model"),
                            device_manufacturer=event.get("metadata").get("device_brand"),
                            carrier=event.get("metadata").get("carrier"),
                            ip_address=event.get("metadata").get("ip_address"),
                            user_agent_data=event.get("metadata").get("user_agent_data"),
                            referer_domain=event.get("metadata").get("referer_domain"),
                            universe_name=universe_name,
                            mw_universe_id=universe_id,
                            supplier_name=supplier_name,
                            mw_supplier_id=supplier_id,
                            offer_name=offer_name,
                            mw_offer_id=offer_id,
                            item_name=item_name,
                            mw_item_id=item_id,
                            item_list=item_list,
                            offer_list=offer_list,
                            search_term=event.get("metadata").get("search_term"),
                            voucher_code=event.get("metadata").get("voucher_code"),
                            voucher_name=event.get("metadata").get("voucher_name"),
                            voucher_value=event.get("metadata").get("voucher_value"),
                            voucher_type=event.get("metadata").get("voucher_type"),
                            basket_amount=event.get("metadata").get("basket_amount"),
                            delivery_amount=event.get("metadata").get("delivery_amount"),
                            please_amount=event.get("metadata").get("please_amount"),
                            partner_amount=event.get("metadata").get("partner_amount"),
                            minimum_basket_amount=event.get("metadata").get("minimum_basket_amount"),
                            delivery_street=event.get("metadata").get("delivery_street"),
                            delivery_zip=event.get("metadata").get("delivery_zip"),
                            delivery_city=event.get("metadata").get("delivery_city"),
                            order_date=event.get("metadata").get("order_date"),
                            odoo_order_id=event.get("metadata").get("order_id"),
                            point_count=event.get("metadata").get("point_count"),
                            link=event.get("metadata").get("link"),
                            campaign_name=event.get("metadata").get("campaign_name"),
                            sent_to_amplitude=False
                        ).save()

                        print("SUCCESS: New " + str(
                            event.get("id")) + " event has been saved to Please Market DB for " + str(customer.email))

                    elif event_number == 1:

                        print("SUCCESS: " + str(
                            event.get("id")) + " event has already been added to Please Market DB for " + str(
                            customer.email))

                    else:
                        print("WARNING: Probably an issue or duplicated events for user " + str(customer.email))

            elif (response.get("type") == "event.list") and (len(response.get("events")) == 0):
                print("WARNING: No event found on Intercom DB for user " + str(customer.email))

            else:
                print("WARNING: Unknown issue for user " + str(customer.email))

            try:
                next_page = response.get("pages").get("next")
                print("Next Page is: " + str(next_page))
            except AttributeError:
                next_page = None
                print("Next Page is: " + str(next_page))
    except:
        print("ERROR: " + str(customer) + " events hasn't been saved to Please Market DB - " + str(sys.exc_info()))
    return


def executor_save_intercom_events_2():
    log_script(name="executor_save_intercom_events_2", status="s")

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(save_intercom_events_2, Customer.objects.filter(
            sign_up_date__gt=datetime.datetime.fromtimestamp(
                float((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))))

    log_script(name="executor_save_intercom_events_2", status="d")
    return


def receive_intercom_events(event):
    event_number = IntercomEvent.objects.filter(intercom_id=event.get("id")).count()
    customer = Customer.objects.get(email=event.get("email"))

    if event_number == 0:

        try:
            item_list = event.get("metadata").get("item_list").split(";")
        except AttributeError:
            item_list = []

        try:
            offer_list = event.get("metadata").get("offer_list").split(";")
        except AttributeError:
            offer_list = []

        try:
            universe_name = event.get("metadata").get("universe_name").lower().replace("_", " ")
            universe_id = event.get("metadata").get("mw_universe_id")
        except AttributeError:
            universe_name = None
            universe_id = None

        try:
            offer_name = event.get("metadata").get("offer_name").lower().replace("_", " ")
            offer_id = event.get("metadata").get("mw_offer_id")
        except AttributeError:
            offer_name = None
            offer_id = None

        try:
            supplier_name = event.get("metadata").get("supplier_name").lower().replace("_", " ")
            supplier_id = event.get("metadata").get("mw_supplier_id")
        except AttributeError:
            supplier_name = None
            supplier_id = None

        try:
            item_name = event.get("metadata").get("item_name").lower().replace("_", " ")
            item_id = event.get("metadata").get("mw_item_id")
        except AttributeError:
            item_name = None
            item_id = None

        IntercomEvent(
            customer=customer,
            neighborhood=customer.neighborhood,
            event_name=event.get("event_name"),
            created_at=datetime.datetime.fromtimestamp(float(event.get("created_at")), timezone('Europe/Paris')),
            user_id=customer.email,
            intercom_user_id=event.get("intercom_user_id"),
            intercom_id=event.get("id"),
            channel="app" if not event.get("metadata").get("from") else event.get("metadata").get("from"),
            app_version=event.get("metadata").get("app_version"),
            os_platform=event.get("metadata").get("os_name"),
            os_name=event.get("metadata").get("os_name"),
            os_version=event.get("metadata").get("os_version"),
            device_brand=event.get("metadata").get("device_brand"),
            device_model=event.get("metadata").get("device_model"),
            device_manufacturer=event.get("metadata").get("device_brand"),
            carrier=event.get("metadata").get("carrier"),
            ip_address=event.get("metadata").get("ip_address"),
            user_agent_data=event.get("metadata").get("user_agent_data"),
            referer_domain=event.get("metadata").get("referer_domain"),
            universe_name=universe_name,
            mw_universe_id=universe_id,
            supplier_name=supplier_name,
            mw_supplier_id=supplier_id,
            offer_name=offer_name,
            mw_offer_id=offer_id,
            item_name=item_name,
            mw_item_id=item_id,
            item_list=item_list,
            offer_list=offer_list,
            search_term=event.get("metadata").get("search_term"),
            voucher_code=event.get("metadata").get("voucher_code"),
            voucher_name=event.get("metadata").get("voucher_name"),
            voucher_value=event.get("metadata").get("voucher_value"),
            voucher_type=event.get("metadata").get("voucher_type"),
            basket_amount=event.get("metadata").get("basket_amount"),
            delivery_amount=event.get("metadata").get("delivery_amount"),
            please_amount=event.get("metadata").get("please_amount"),
            partner_amount=event.get("metadata").get("partner_amount"),
            minimum_basket_amount=event.get("metadata").get("minimum_basket_amount"),
            delivery_street=event.get("metadata").get("delivery_street"),
            delivery_zip=event.get("metadata").get("delivery_zip"),
            delivery_city=event.get("metadata").get("delivery_city"),
            order_date=event.get("metadata").get("order_date"),
            odoo_order_id=event.get("metadata").get("order_id"),
            point_count=event.get("metadata").get("point_count"),
            link=event.get("metadata").get("link"),
            campaign_name=event.get("metadata").get("campaign_name"),
            sent_to_amplitude=False
        ).save()

        print("SUCCESS: New " + str(event.get("id")) + " event has been saved to Please Market DB for " + str(
            customer.email))

        if event.get("event_name") == "validated basket 1":
            retrieve_vb1(event=IntercomEvent.objects.get(intercom_id=event.get("id")))

            print("SUCCESS: New " + str(event.get("id")) + " validated basket 1 event has been retrieved for " + str(
                customer.email))

    elif event_number == 1:

        print("SUCCESS: " + str(event.get("id")) + " event has already been added to Please Market DB for " + str(
            customer.email))

    else:
        print("WARNING: Probably an issue or duplicated events for user " + str(customer.email))

    return


def update_intercom_users(customer):

    try:
        url = "https://api.intercom.io/users"

        custom_attributes = {
            "signed_up": "" if not customer.signed_up else customer.signed_up,
            "sharable_user_id": "" if not customer.sharable_user_id else customer.sharable_user_id,
            "first_name": "" if not customer.first_name else customer.first_name,
            "last_name": "" if not customer.last_name else customer.last_name,
            "profile_picture": "" if not customer.profile_picture else customer.profile_picture,
            "street": "" if not customer.street else customer.street,
            "zip": "" if not customer.zip else customer.zip,
            "city": "" if not customer.city else customer.city,
            "w_longitude": "" if not customer.w_longitude else customer.w_longitude,
            "w_latitude": "" if not customer.w_latitude else customer.w_latitude,
            "age": "" if not customer.age else customer.age,
            "gender": "" if not customer.gender else customer.gender,
            "neighborhood": "" if not customer.neighborhood else customer.neighborhood.name,
            "neighborhood_odoo_id": "" if not customer.neighborhood else customer.neighborhood.odoo_id,
            "neighborhood_mw_id": "" if not customer.neighborhood else customer.neighborhood.mw_id,
            "family": "" if not customer.family else customer.family,
            "cb": "" if not customer.cb else customer.cb[0],
            "company": "" if not customer.company else customer.company,
            "job_title": "" if not customer.job_title else customer.job_title,
            "orders_number": "" if not customer.orders_number else customer.orders_number,
            "last_order_date": "" if not customer.last_order_date else customer.last_order_date.strftime("%s"),
            "average_basket": "" if not customer.average_basket else customer.average_basket,
            "average_rating": "" if not customer.average_rating else customer.average_rating,
            "total_voucher": "" if not customer.total_voucher else customer.total_voucher,
            "total_spent": "" if not customer.total_spent else customer.total_spent,
            "test_user": "" if not customer.test_user else customer.test_user,
            "app_version": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].app_version,
            "os_platform": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].os_platform,
            "os_name": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].os_name,
            "os_version": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].os_version,
            "device_brand": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].device_brand,
            "device_model": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].device_model,
            "device_manufacturer": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].device_manufacturer,
            "carrier": "" if not IntercomEvent.objects.filter(customer=customer) else
            IntercomEvent.objects.filter(customer=customer).order_by("-created_at")[0].carrier,
            "last_order_at": "" if not customer.last_order_date else customer.last_order_date.strftime("%s"),
            "referral_code": "" if not customer.referral_code else customer.referral_code,
            "referral_leads_counter": "" if not customer.referral_leads_counter else customer.referral_leads_counter,
            "referral_counter": "" if not customer.referral_counter else customer.referral_counter,
            "marketing": True if customer.marketing is None else customer.marketing,
            "archived": False if customer.archived is None else customer.archived,
            "baned": False if customer.baned is None else customer.baned,
        }

        payload = {
            "user_id": customer.email,
            "email": customer.email,
            "phone": customer.phone,
            "name": str(str("" if not customer.first_name else customer.first_name) + " " + str(
                "" if not customer.last_name else customer.last_name)),
            "signed_up_at": "" if not customer.sign_up_date else customer.sign_up_date.strftime("%s"),
            "custom_attributes": custom_attributes,
        }

        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': str(settings.INTERCOM_KEY),
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        if response.json().get("type") == "error.list":
            print("ERROR: " + str(customer.email) + " - error.list from Intercom - " + response.json().get("type"))

        elif response.json().get("type") == "user":
            print("SUCCESS: " + str(customer.email) + " has been uptaded to Intercom DB")

        else:
            print("ERROR: " + str(customer.email) + " hasn't been uptaded to Intercom DB - unexpected error")

    except:
        print(str("ERROR: " + str(customer.email) + " hasn't been uptaded to Intercom DB - " + str(sys.exc_info())))

    return


# from please_marketing_app.main_scripts.intercom import *
def executor_update_intercom_users():
    log_script(name="executor_update_intercom_users", status="s")

    with ThreadPoolExecutor(max_workers=4) as executor:
        inclusion_list = list(
            IntercomEvent.objects.filter(
                neighborhood__isnull=False,
                customer__isnull=False,
                customer__email__isnull=False,
                created_at__gt=datetime.datetime.fromtimestamp(
                    float((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))
            ).distinct("customer__id").values_list("customer__id", flat=True)
        )

        executor.map(update_intercom_users, Customer.objects.filter(id__in=inclusion_list))

    log_script(name="executor_update_intercom_users", status="d")
    return


def update_local_users(customer):
    try:

        url = str("https://api.intercom.io/users?email=" + customer.email)
        headers = {
            "Authorization": str(settings.INTERCOM_KEY),
            "Accept": "application/json"
        }

        response_raw = requests.request("GET", url, headers=headers).json()

        if response_raw.get("total_count") == 1:

            response = response_raw.get("users")[0]

            customer.last_request_at = None if not response.get("last_request_at") else datetime.datetime.fromtimestamp(
                float(response.get("last_request_at")), timezone('Europe/Paris'))
            customer.last_seen_ip = None if not response.get("last_seen_ip") else response.get("last_seen_ip")
            customer.unsubscribed_from_emails = False if not response.get("unsubscribed_from_emails") else response.get(
                "unsubscribed_from_emails")
            customer.session_count = 0 if not response.get("session_count") else int(response.get("session_count"))
            customer.intercom_id = None if not response.get("id") else response.get("id")
            customer.user_agent_data = None if not response.get("user_agent_data") else response.get("user_agent_data")
            customer.social_profiles_intercom = None if not response.get("social_profiles").get(
                "social_profiles") else response.get("social_profiles").get("social_profiles")

            customer.save()

            print("SUCCESS: " + str(customer.email) + " has been updated to Please Market DB")

        elif response_raw.get("total_count") == 0:
            print("WARNING: " + str(customer.email) + " hasn't been updated to Please Market DB (not found in Intercom DB)")

        elif response_raw.get("total_count") > 1:
            print("WARNING: " + str(customer.email) + " hasn't been updated to Please Market DB (duplicate user in Intercom DB)")

    except:
        print("ERROR: " + str(customer.email) + " hasn't been updated to Please Market DB - " + str(sys.exc_info()))

    return


# from please_marketing_app.main_scripts.intercom import *
def executor_update_local_users():
    log_script(name="executor_update_local_users", status="s")

    with ThreadPoolExecutor(max_workers=4) as executor:
        inclusion_list = list(
            IntercomEvent.objects.filter(
                neighborhood__isnull=False,
                customer__isnull=False,
                customer__email__isnull=False,
                created_at__gt=datetime.datetime.fromtimestamp(
                    float((datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%s")))
            ).distinct("customer__id").values_list("customer__id", flat=True)
        )

        executor.map(update_local_users, Customer.objects.filter(id__in=inclusion_list))

    log_script(name="executor_update_local_users", status="d")
    return
