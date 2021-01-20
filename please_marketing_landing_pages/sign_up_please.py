# coding: utf-8

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.template import loader
import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import hashlib
import hmac
import random
import random
from twilio.rest import Client
import emoji
from django.conf import settings
from django.db.models import Q
import sys
from django.template.loader import render_to_string
from please_marketing_app.models import SmsHistory, Merchant, Customer, Merchant, Neighborhood
from please_marketing_app.get_vouchers.get_voucher_instore_signup import get_one_voucher_options
from .models import Lead
import unicodedata
import requests
from rq import Queue
from worker_urgent_tasks import conn_urgent_tasks


# from please_marketing_landing_pages.sign_up_please import *
def get_cgu():
    url = "https://mw.please-it.com/next-mw/api/public/cgu/valid"

    querystring = {
        "type": "CGUH",
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    return response


def get_address(address):

    customer_query = str(address)

    url = "https://maps.googleapis.com/maps/api/geocode/json"

    querystring = {
        "address": str(customer_query.replace(" ", "+")),  # "1600+Amphitheatre+Parkway,+Mountain+View,+CA",
        "key": str(settings.GOOGLE_GEOCODING_KEY)
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    if response.get("status") == "OK":
        results = response.get("results")[0]
        add_comp = results.get("address_components")

        latitude = results.get("geometry").get("location").get("lat")
        longitude = results.get("geometry").get("location").get("lng")
        street_number = ""
        route = ""
        locality = ""
        postal_code = ""

        for comp in add_comp:
            if comp.get("types")[0] == "street_number":
                street_number = comp.get("long_name")

            elif comp.get("types")[0] == "route":
                route = comp.get("long_name")

            elif comp.get("types")[0] == "locality":
                locality = comp.get("long_name")

            elif comp.get("types")[0] == "postal_code":
                postal_code = comp.get("long_name")

            else:
                continue

        street = str(street_number) + " " + str(route)
        city = str(locality)
        zip = str(postal_code)

        return latitude, longitude, street, city, zip


def get_neighborhood(latitude, longitude):

    url = "https://mw.please-it.com/next-mw/api/public/website/conciergerie/coordinates"

    querystring = {
        "longitude": str(longitude),
        "latitude": str(latitude),
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    return response.get("odooConciergerieId")


def send_sms_fail_password_or_email(first_name, phone):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    try:
        message = client.messages.create(
            str(phone),
            body=str(
                str("Bonjour ")
                + str(first_name)
                + str(", malheureusement la création de votre compte Please n'a pas pu être finalisée car votre adresse "
                      "email est déjà utilisée par un autre compte. Merci de réessayer avec une nouvelle adresse.")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: send_sms_fail_password_or_email sent to user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - In-Store Sign Up (failed pwd or email)"
        ).save()

    except:
        print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def send_sms_fail_password(first_name, phone):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    try:
        message = client.messages.create(
            str(phone),
            body=str(
                str("Bonjour ")
                + str(first_name)
                + str(", malheureusement la création de votre compte Please n'a pas pu être finalisée car votre "
                      "mot de passe ne respecte pas notre politique de sécurité. Merci de réessayer avec un "
                      "mot de passe comprenant 8 caractères, 1 majuscule et 1 chiffre minimum.")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: send_sms_fail_password sent to user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - In-Store Sign Up (failed pwd)"
        ).save()

    except:
        print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def sign_up_please(
        email,
        first_name,
        last_name,
        pwd,
        phone,
        street,
        city,
        zip,
        longitude,
        latitude,
        odoo_conciergerie_id,
        cgu_id,
        marketing):

    now = datetime.datetime.now()
    cgu_date = str(now.strftime("%Y-%m-%dT%H:%M:%S"))

    try:

        url = "https://mw.please-it.com/next-mw/api/public/user"

        payload = {
            "developerMode": False,
            "marketingSubscription": marketing,
            "subscribed": False,
            "email": str(email),
            "pwd": str(pwd),
            "billingAddress": {
                "street": str(street),  # "12 Rue de la Mairie",
                "city": str(city),  # "Mantes-la-Ville",
                "zip": str(zip),  # "78711",
                "type": "housenumber",
                "label": str(str(street) + " " + str(zip) + " " + str(city)),  # "12 Rue de la Mairie 78711 Mantes-la-Ville",
                "coordinate": {
                    "longitude": longitude,  # 1.712679,
                    "latitude": latitude,  # 48.978537
                },
                "building": "",
                "digicode": "",
                "floor": "",
                "elevator": "",
                "door": "",
                "details": ""
            },
            "linkedToConciergerie": True,
            "odooConciergerieId": int(odoo_conciergerie_id),  # 4,
            "firstName": str(first_name),
            "lastName": str(last_name),
            "mobileNumber": str(phone),  # "0677543333",
            "cguDate": cgu_date,  # "2019-01-10T01:32:14",
            "cguId": int(cgu_id),  # 102,
            "cguValid": True
        }

        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'X-Accept-Version': "1.9",
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers).json()

        if response.get("statusCode") == 500:
            print("ERROR: Not able to create a user through on-site sign-up process - ERREUR 500 from Please")
            send_sms_fail_password_or_email(first_name=first_name, phone=phone)

        if response.get("statusCode") == 400:
            print("ERROR: Not able to create a user through on-site sign-up process - ERREUR 400 from Please")
            send_sms_fail_password(first_name=first_name, phone=phone)

        else:
            odoo_user_id = response.get("odooId")
            return odoo_user_id

    except:
        print("ERROR: Not able to create a user through on-site sign-up process - " + str(sys.exc_info()))
        send_sms_fail_password_or_email(first_name=first_name, phone=phone)

    return


def get_voucher(neighborhood, odoo_user_id):

    voucher_code = get_one_voucher_options(
        customer_id=int(odoo_user_id),
        notification_type="Landing Page Signup",
        voucher_name=str("Coupon Première Commande Landing Page - " + str(neighborhood.name)),
        voucher_validity=30,
        voucher_value=5,
        voucher_val_type='amount',
        voucher_code=0,
        first_order_only=True,
        first_customer_order=True,
        pricelist_id=False,
        minimum_cart_amount=20,
    )[0]

    return voucher_code


def send_sms(first_name, phone, neighborhood, odoo_user_id):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    voucher_code = get_voucher(
        neighborhood=neighborhood,
        odoo_user_id=odoo_user_id
    )

    try:
        message = client.messages.create(
            str(phone),
            body=str(
                str("Bonjour ")
                + str(first_name)
                + str(" ! Bienvenue sur Please, votre compte a bien été créé ")
                + emoji.emojize(u':heart_eyes:', use_aliases=True)
                + str("\n")
                + str("Bénéficiez de 5€ pour votre première livraison Please avec le code " + str(voucher_code) + " (valable 30 jours) !")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: SMS properly sent to newly created in-store user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - Landing Page Sign Up"
        ).save()

    except:
        print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def send_sms_fail_phone(first_name, phone):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    try:
        message = client.messages.create(
            str(phone),
            body=str(
                str("Bonjour ")
                + str(first_name)
                + str(", malheureusement la création de votre compte Please n'a pas pu être finalisée car votre numéro "
                      "de téléphone est déjà utilisé par un autre compte. Merci de réessayer avec un nouveau numéro.")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: send_sms_fail_phone sent to user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - Landing Page Sign Up (failed phone)"
        ).save()

    except:
        print("ERROR: Twilio API Error - Message not sent " + " - " + str(sys.exc_info()))

    return


def update_intercom_user(email, first_name, last_name, phone, neighborhood, street, city, zip, longitude, latitude, marketing, sign_up_date):
        try:
            url = "https://api.intercom.io/users"

            custom_attributes = {
                "signed_up": False if sign_up_date == "" else True,
                "first_name": first_name,
                "last_name": last_name,
                "street": street,
                "zip": zip,
                "city": city,
                "w_longitude": longitude,
                "w_latitude": latitude,
                "neighborhood": neighborhood.name,
                "neighborhood_odoo_id": neighborhood.odoo_id,
                "neighborhood_mw_id": neighborhood.mw_id,
                "marketing": marketing,
                "archived": False,
            }

            payload = {
                "user_id": email,
                "email": email,
                "phone": phone,
                "name": str(str(first_name) + " " + str(last_name)),
                "signed_up_at": sign_up_date,  # sign_up_date.strftime("%s")
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
                print("ERROR: " + str(email) + " - error.list from Intercom - " + response.json().get("type"))

            elif response.json().get("type") == "user":
                print("SUCCESS: " + str(email) + " has been created in Intercom DB from landing pages")

            else:
                print("ERROR: " + str(email) + " hasn't been created in Intercom DB from landing pages - unexpected error")

        except:
            print(str("ERROR: " + str(email) + " hasn't been created in Intercom DB from landing pages - " + str(sys.exc_info())))

        return


def track_event(event_name, email, metadata):
        try:

            url = "https://api.intercom.io/events"

            # METADATA FORMAT
            # metadata = {
            #    "data": "data",
            # }

            payload = {
                "event_name": event_name,
                "created_at": datetime.datetime.now().strftime("%s"),
                "user_id": email,
                "metadata": metadata,
            }

            print(payload)

            headers = {
                'accept': "application/json",
                'content-type': "application/json",
                'authorization': str(settings.INTERCOM_KEY),
                'cache-control': "no-cache"
            }

            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

            print("SUCCESS: " + str(event_name) + " has been created in Intercom DB from landing pages for " + str(email))

        except:
            print(str("ERROR: " + str(email) + " hasn't been uptaded to Intercom DB - " + str(sys.exc_info())))

        return


def verif_phone(phone):

    url = "https://mw.please-it.com/next-mw/api/public/user/mobileNumber/exists"

    querystring = {
        "mobileNumber": str(phone),  # "0622695505"
    }

    payload = ""
    headers = {
        'cache-control': "no-cache",
        }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

    return response


def sign_up_lead(email, password, first_name, last_name, phone, address_raw, neighborhood, img_name, txt_name, search_term, marketing):
        lead = Lead(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            raw_address=address_raw,
            neighborhood=neighborhood,
            img_name=img_name,
            txt_name=txt_name,
            search_term=search_term,
        )
        lead.save()

        update_intercom_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            neighborhood=neighborhood,
            street="",
            city="",
            zip="",
            longitude="",
            latitude="",
            marketing=marketing,
            sign_up_date="",
        )

        if verif_phone(phone=phone) is False:
            try:
                cgu = get_cgu()

                address = get_address(address=address_raw)

                latitude = address[0]
                longitude = address[1]
                street = address[2]
                city = address[3]
                zip = address[4]

                new_signed_up = sign_up_please(
                    email=email,
                    pwd=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    street=street,
                    city=city,
                    zip=zip,
                    latitude=latitude,
                    longitude=longitude,
                    odoo_conciergerie_id=neighborhood.odoo_id,
                    cgu_id=cgu.get("id"),
                    marketing=marketing,
                )

                if new_signed_up:
                    lead.odoo_user_id = new_signed_up
                    lead.signed_up_please = True
                    lead.street = street
                    lead.city = city
                    lead.zip = zip
                    lead.save()

                    update_intercom_user(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        neighborhood=neighborhood,
                        street=street,
                        city=city,
                        zip=zip,
                        longitude=longitude,
                        latitude=latitude,
                        marketing=marketing,
                        sign_up_date=datetime.datetime.now().strftime("%s"),
                    )

                    track_event(
                        event_name="completed in city sign up form",
                        email=email,
                        metadata={
                            "neighborhood": neighborhood.name,
                        }
                    )

                    send_sms(
                        first_name=first_name,
                        phone=str(phone),
                        neighborhood=neighborhood,
                        odoo_user_id=new_signed_up
                    )

            except:
                print("ERROR: " + str(sys.exc_info()))
        else:
            send_sms_fail_phone(first_name=first_name, phone=phone)
        return
