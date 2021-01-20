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
from .forms import SignUpForm
import random
from twilio.rest import Client
import emoji
from django.conf import settings
from django.db.models import Q
import sys
from django.template.loader import render_to_string
from please_marketing_app.models import Customer, Merchant, Neighborhood
from please_marketing_growth_hack.models import Lead, GameVoucher
from please_marketing_growth_hack.merchant_sign_up.verif_phone import verif_phone
from please_marketing_growth_hack.merchant_sign_up.get_neighborhood import get_neighborhood
from please_marketing_growth_hack.merchant_sign_up.get_cgu import get_cgu
from please_marketing_growth_hack.merchant_sign_up.get_address import get_address
from please_marketing_growth_hack.merchant_sign_up.sign_up import sign_up_please
from please_marketing_app.models import SmsHistory, Merchant
from please_marketing_app.get_vouchers.get_voucher_instore_signup import get_one_voucher_options
import unicodedata
import requests
from rq import Queue
from worker_urgent_tasks import conn_urgent_tasks


def get_voucher(neighborhood, odoo_user_id):

    voucher_code = get_one_voucher_options(
        customer_id=int(odoo_user_id),
        notification_type="In-City Signup",
        voucher_name=str("Coupon Première Commande In-City - " + str(neighborhood.name)),
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
            sms_type="Campaign - In-City Sign Up"
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
            sms_type="Campaign - In-City Sign Up (failed phone)"
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
                print("SUCCESS: " + str(email) + " has been created in Intercom DB from in store sign up")

            else:
                print("ERROR: " + str(email) + " hasn't been created in Intercom DB from in store sign up - unexpected error")

        except:
            print(str("ERROR: " + str(email) + " hasn't been created in Intercom DB from in store sign up - " + str(sys.exc_info())))

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

            print("SUCCESS: " + str(event_name) + " has been created in Intercom DB from in store sign up for " + str(email))

        except:
            print(str("ERROR: " + str(email) + " hasn't been uptaded to Intercom DB - " + str(sys.exc_info())))

        return


def sign_up_lead(email, password, first_name, last_name, phone, address_raw, neighborhood, marketing):
        Lead(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            raw_address=address_raw,
        ).save()

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

                    lead = Lead.objects.filter(email=email, phone=phone).order_by("-created_date").first()

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


def sign_up(request):

    nb_id = 2 if not request.GET.get('nb_id', '') else request.GET.get('nb_id', '')

    neighborhood = Neighborhood.objects.filter().last() if not Neighborhood.objects.filter(mw_id=int(nb_id)) else Neighborhood.objects.filter(mw_id=int(nb_id)).first()   # else Merchant.objects.filter(mw_offer_id=int(mw_offer_id)).first()

    if request.method == 'POST':
        form_sign_up = SignUpForm(data=request.POST)

        if form_sign_up.is_valid():
            email = form_sign_up.cleaned_data["email"]
            password = form_sign_up.cleaned_data["password"]
            first_name = form_sign_up.cleaned_data["first_name"]
            last_name = form_sign_up.cleaned_data["last_name"]
            country_code = form_sign_up.cleaned_data["country_code"]
            phone_raw = form_sign_up.cleaned_data["phone"]
            address_raw = form_sign_up.cleaned_data["address"]

            phone = str(country_code + phone_raw.lstrip("0"))

            marketing = True if form_sign_up.cleaned_data["marketing"] == "True" else False

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(sign_up_lead, args=(email, password, first_name, last_name, phone, address_raw, neighborhood, marketing), timeout=30)

            return redirect('/inscription/merci_ville' + '?nb_id=' + str(nb_id))

        else:
            context = {
                "nb_id": nb_id,
            }

            template = loader.get_template('please_marketing_growth_hack/invalid_form_in_city.html')
            return HttpResponse(template.render(context, request))

    else:

        context = {
            "form_sign_up": SignUpForm(),
            "nb_id": nb_id,
        }

        template = loader.get_template('please_marketing_growth_hack/sign_up_in_city.html')
        return HttpResponse(template.render(context, request))


def thanks(request):
    nb_id = request.GET.get('nb_id', '')
    context = {
        'nb_id': nb_id
    }
    template = loader.get_template('please_marketing_growth_hack/thanks_in_city.html')
    return HttpResponse(template.render(context, request))


def invalid_form(request):
    nb_id = request.GET.get('nb_id', '')
    context = {
        'nb_id': nb_id
    }
    template = loader.get_template('please_marketing_growth_hack/invalid_form_in_city.html')
    return HttpResponse(template.render(context, request))


def error(request):
    context = {
    }
    template = loader.get_template('please_marketing_growth_hack/404.html')
    return HttpResponse(template.render(context, request))
