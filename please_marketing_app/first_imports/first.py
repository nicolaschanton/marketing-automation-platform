# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, IntercomEvent, Neighborhood, Fete
import requests
import datetime
from pytz import timezone
from django.conf import settings
from bs4 import BeautifulSoup


def import_feast():

    months = [
        ('janvier', 1),
        ('fevrier', 2),
        ('mars', 3),
        ('avril', 4),
        ('mai', 5),
        ('juin', 6),
        ('juillet', 7),
        ('aout', 8),
        ('septembre', 9),
        ('octobre', 10),
        ('novembre', 11),
        ('decembre', 12),
    ]

    for month in [month1[0] for month1 in months]:
        dict_month = dict(months)

        url = str("http://tonprenom.com/fetes/" + month)

        response = requests.get(url).text
        tab = BeautifulSoup(response, 'html.parser')

        for fd in tab.find_all(class_="fd"):
            fd2 = BeautifulSoup(str(fd), 'html.parser')
            for fd3 in fd2.find_all("a"):
                try:
                    first_name = str(fd3.get_text())
                    date = str(fd.find("span").find("b").get_text())
                    date_int = int(date)
                    month_int = int(dict_month[month])
                    print(first_name + " - " + date + " " + month)

                    Fete(
                        first_name=first_name,
                        month=month_int,
                        day=date_int,
                    ).save()

                except:
                    continue

    return


def save_intercom_events():
    for customer in Customer.objects.filter(email__isnull=False, first_import_events_done=False):
        print("Current user working on is: " + str(customer.email))
        next_page = str("https://api.intercom.io/events?type=user&email="
                        + customer.email
                        + "&since=" + str((datetime.datetime.today() - datetime.timedelta(days=200)).strftime("%s")))

        while next_page is not None:
            url = next_page
            headers = {
                "Authorization": str(settings.INTERCOM_KEY),
                "Accept": "application/json"
            }

            response = requests.request("GET", url, headers=headers).json()

            print(response)

            if response.get("type") == "event.list":

                for event in response.get("events"):
                    event_raw = IntercomEvent.objects.filter(intercom_id=event.get("id"))
                    event_number = event_raw.count()

                    print(event_number)

                    if event_number == 0:

                        try:
                            item_list = event.get("metadata").get("item_list").split(";")
                        except AttributeError:
                            item_list = []

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
                            app_version=event.get("metadata").get("app_version"),
                            os_platform=event.get("metadata").get("os_name"),
                            os_name=event.get("metadata").get("os_name"),
                            os_version=event.get("metadata").get("os_version"),
                            device_brand=event.get("metadata").get("device_brand"),
                            device_model=event.get("metadata").get("device_model"),
                            device_manufacturer=event.get("metadata").get("device_brand"),
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
                            voucher_code=event.get("metadata").get("voucher_code"),
                            voucher_name=event.get("metadata").get("voucher_name"),
                            voucher_value=event.get("metadata").get("voucher_value"),
                            basket_amount=event.get("metadata").get("basket_amount"),
                            delivery_amount=event.get("metadata").get("delivery_amount"),
                            please_amount=event.get("metadata").get("please_amount"),
                            partner_amount=event.get("metadata").get("partner_amount"),
                            minimum_basket_amount=event.get("metadata").get("minimum_basket_amount"),
                            delivery_street=event.get("metadata").get("delivery_street"),
                            delivery_zip=event.get("metadata").get("delivery_zip"),
                            delivery_city=event.get("metadata").get("delivery_city"),
                            order_date=event.get("metadata").get("order_date"),
                            point_count=event.get("metadata").get("point_count"),
                            link=event.get("metadata").get("link"),
                            campaign_name=event.get("metadata").get("campaign_name"),
                            search_term=event.get("metadata").get("search_term"),
                            sent_to_amplitude=False
                            ).save()

                        print("SUCCESS: New " + str(event.get("id")) + " event has been saved to Please Market DB for " + str(customer.email))

                    elif event_number == 1:

                        print("SUCCESS: " + str(event.get("id")) + " event has already been added to Please Market DB for " + str(customer.email))

                    else:
                        print("WARNING: Probably an issue or duplicated events for user " + str(customer.email))

            else:
                print("WARNING: No event found on Intercom DB for " + str(customer.email))

            try:
                next_page = response.get("pages").get("next")
                print("Next Page is: " + str(next_page))
            except AttributeError:
                next_page = None
                print("Next Page is: " + str(next_page))

        customer.first_import_events_done = True
        customer.save()

    return
