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
from .forms import SignUpForm, GameVoucherVernonForm
import random
from twilio.rest import Client
import emoji
from django.conf import settings
from django.db.models import Q
import sys
from django.template.loader import render_to_string
from please_marketing_app.models import Customer, Merchant, Neighborhood
from please_marketing_growth_hack.models import Lead, GameVoucher, GameVoucherVernon
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
from django.core.mail import EmailMessage


def get_voucher(odoo_offer_id, merchant_name, odoo_user_id):

    voucher_code = get_one_voucher_options(
        customer_id=int(odoo_user_id),
        notification_type="In-Store Signup",
        voucher_name=str("Coupon Première Commande In-Store - " + str(merchant_name)),
        voucher_validity=30,
        voucher_value=5,
        voucher_val_type='amount',
        voucher_code=0,
        first_order_only=True,
        first_customer_order=True,
        pricelist_id=int(odoo_offer_id),
        minimum_cart_amount=20,
    )[0]

    return voucher_code


def send_sms(first_name, phone, odoo_offer_id, merchant_name, odoo_user_id):

    # Your Account Sid and Auth Token from twilio.com/user/account
    account_sid = str(settings.TWILIO_SID)
    auth_token = str(settings.TWILIO_TOKEN)
    client = Client(account_sid, auth_token)
    from_phone = str(settings.TWILIO_PHONE)

    voucher_code = get_voucher(
        odoo_offer_id=odoo_offer_id,
        merchant_name=merchant_name,
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
                + str("Bénéficiez de 5€ pour votre première livraison Please chez " + str(merchant_name) + " avec le code " + str(voucher_code) + " (valable 30 jours) !")
                + str("\n")
                + str("Pour télécharger l'App : www.pleaseapp.com")
            ),
            from_=from_phone
        )

        print("SUCCESS: SMS properly sent to newly created in-store user ", phone, message.sid, message.date_created.date, message.body)

        SmsHistory(
            content=message.body,
            send_date=datetime.datetime.now(),
            sms_type="Campaign - In-Store Sign Up"
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
            sms_type="Campaign - In-Store Sign Up (failed phone)"
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


def sign_up_lead(email, password, first_name, last_name, phone, address_raw, merchant, marketing):
        Lead(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            raw_address=address_raw,
            merchant=merchant,
        ).save()

        update_intercom_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            neighborhood=merchant.neighborhood,
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
                    odoo_conciergerie_id=merchant.neighborhood.odoo_id,
                    cgu_id=cgu.get("id"),
                    marketing=marketing
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
                        neighborhood=merchant.neighborhood,
                        street=street,
                        city=city,
                        zip=zip,
                        longitude=longitude,
                        latitude=latitude,
                        marketing=marketing,
                        sign_up_date=datetime.datetime.now().strftime("%s"),
                    )

                    track_event(
                        event_name="completed in store sign up form",
                        email=email,
                        metadata={
                            "merchant_mw_offer_id": merchant.mw_offer_id,
                            "merchant_name": merchant.name,
                            "neighborhood": merchant.neighborhood.name,
                        }
                    )

                    send_sms(
                        first_name=first_name,
                        phone=str(phone),
                        odoo_offer_id=merchant.odoo_offer_id,
                        merchant_name=merchant.name,
                        odoo_user_id=new_signed_up
                    )

            except:
                print("ERROR: " + str(sys.exc_info()))
        else:
            send_sms_fail_phone(first_name=first_name, phone=phone)
        return


def sign_up(request):

    mw_offer_id = 1 if not request.GET.get('mw_offer_id', '') else request.GET.get('mw_offer_id', '')

    merchant = Merchant.objects.filter(mw_offer_id=int(mw_offer_id)).first()   # else Merchant.objects.filter(mw_offer_id=int(mw_offer_id)).first()
    merchant_name = merchant.name
    merchant_mw_id = merchant.mw_offer_id

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
            q_urgent_tasks.enqueue(sign_up_lead, args=(email, password, first_name, last_name, phone, address_raw, merchant, marketing), timeout=30)

            return redirect('/inscription/merci' + '?mw_offer_id=' + str(mw_offer_id))

        else:
            context = {
                "mw_offer_id": mw_offer_id,
            }

            template = loader.get_template('please_marketing_growth_hack/invalid_form.html')
            return HttpResponse(template.render(context, request))

    else:

        context = {
            "form_sign_up": SignUpForm(),
            "merchant_name": merchant_name,
            "merchant_mw_id": merchant_mw_id,
        }

        template = loader.get_template('please_marketing_growth_hack/sign_up.html')
        return HttpResponse(template.render(context, request))


def thanks(request):
    mw_offer_id = request.GET.get('mw_offer_id', '')
    context = {
        'mw_offer_id': mw_offer_id
    }
    template = loader.get_template('please_marketing_growth_hack/thanks.html')
    return HttpResponse(template.render(context, request))


def invalid_form(request):
    mw_offer_id = request.GET.get('mw_offer_id', '')
    context = {
        'mw_offer_id': mw_offer_id
    }
    template = loader.get_template('please_marketing_growth_hack/invalid_form.html')
    return HttpResponse(template.render(context, request))


def error(request):
    context = {
    }
    template = loader.get_template('please_marketing_growth_hack/404.html')
    return HttpResponse(template.render(context, request))


def game(request):
    email_raw = request.GET.get('user', '')

    if email_raw is None:
        pass

    else:
        customer = Customer.objects.filter(email=email_raw).first()
        merchant_target = Merchant.objects.filter(neighborhood=customer.neighborhood, odoo_offer_id__isnull=False, active=True).order_by("?").first()
        coin = random.randint(1, 4)

        if GameVoucher.objects.filter(customer=customer).count() == 0:

            if coin == 1:
                voucher_code = get_one_voucher_options(
                    customer_id=customer.odoo_user_id,
                    minimum_cart_amount=20,
                    first_customer_order=False,
                    first_order_only=True,
                    voucher_val_type='amount',
                    voucher_value=10,
                    voucher_validity=7,
                    voucher_name=str("Coupon Jeu Tirage au Sort - " + str(customer.email)),
                    notification_type="Coupon Jeu Tirage au Sort",
                    pricelist_id=merchant_target.odoo_offer_id,
                    voucher_code=0
                )[0]

                title = str(customer.first_name + ", vous avez gagné 10€ chez " + merchant_target.name + " !")

                text = str("Bon d'achat de 10€ valable 7 jours pour toute commande supérieure à 20€ avec le code : " + voucher_code + " 😍")

                GameVoucher(
                    customer=customer,
                    voucher_code=voucher_code,
                    merchant=merchant_target,
                    voucher_value=10,
                ).save()

                context = {
                    'title': title,
                    'text': text,
                    'merchant_id': merchant_target.mw_offer_id,
                }
                template = loader.get_template('please_marketing_growth_hack/game.html')
                return HttpResponse(template.render(context, request))

            elif coin == 2:
                voucher_code = get_one_voucher_options(
                    customer_id=customer.odoo_user_id,
                    minimum_cart_amount=20,
                    first_customer_order=False,
                    first_order_only=True,
                    voucher_val_type='amount',
                    voucher_value=2,
                    voucher_validity=7,
                    voucher_name=str("Coupon Jeu Tirage au Sort - " + str(customer.email)),
                    notification_type="Coupon Jeu Tirage au Sort",
                    pricelist_id=merchant_target.odoo_offer_id,
                    voucher_code=0
                )[0]

                title = str(customer.first_name + ", vous avez gagné 2€ chez " + merchant_target.name + " !")

                text = str("Bon d'achat de 2€ valable 7 jours pour toute commande supérieure à 20€ avec le code : " + voucher_code + " 😍")

                GameVoucher(
                    customer=customer,
                    voucher_code=voucher_code,
                    merchant=merchant_target,
                    voucher_value=2,
                ).save()

                context = {
                    'title': title,
                    'text': text,
                    'merchant_id': merchant_target.mw_offer_id,
                }
                template = loader.get_template('please_marketing_growth_hack/game.html')
                return HttpResponse(template.render(context, request))

            elif coin == 3:
                voucher_code = get_one_voucher_options(
                    customer_id=customer.odoo_user_id,
                    minimum_cart_amount=20,
                    first_customer_order=False,
                    first_order_only=True,
                    voucher_val_type='amount',
                    voucher_value=3,
                    voucher_validity=7,
                    voucher_name=str("Coupon Jeu Tirage au Sort - " + str(customer.email)),
                    notification_type="Coupon Jeu Tirage au Sort",
                    pricelist_id=merchant_target.odoo_offer_id,
                    voucher_code=0
                )[0]

                title = str(customer.first_name + ", vous avez gagné 3€ chez " + merchant_target.name + " !")

                text = str("Bon d'achat de 3€ valable 7 jours pour toute commande supérieure à 20€ avec le code : " + voucher_code + " 😍")

                GameVoucher(
                    customer=customer,
                    voucher_code=voucher_code,
                    merchant=merchant_target,
                    voucher_value=3,
                ).save()

                context = {
                    'title': title,
                    'text': text,
                    'merchant_id': merchant_target.mw_offer_id,
                }
                template = loader.get_template('please_marketing_growth_hack/game.html')
                return HttpResponse(template.render(context, request))

            elif coin == 4:
                voucher_code = get_one_voucher_options(
                    customer_id=customer.odoo_user_id,
                    minimum_cart_amount=20,
                    first_customer_order=False,
                    first_order_only=True,
                    voucher_val_type='amount',
                    voucher_value=5,
                    voucher_validity=7,
                    voucher_name=str("Coupon Jeu Tirage au Sort - " + str(customer.email)),
                    notification_type="Coupon Jeu Tirage au Sort",
                    pricelist_id=merchant_target.odoo_offer_id,
                    voucher_code=0
                )[0]

                title = str(customer.first_name + ", vous avez gagné 5€ chez " + merchant_target.name + " !")

                text = str(
                    "Bon d'achat de 5€ valable 7 jours pour toute commande supérieure à 20€ avec le code : " + voucher_code + " 😍")

                GameVoucher(
                    customer=customer,
                    voucher_code=voucher_code,
                    merchant=merchant_target,
                    voucher_value=5,
                ).save()

                context = {
                    'title': title,
                    'text': text,
                    'merchant_id': merchant_target.mw_offer_id,
                }
                template = loader.get_template('please_marketing_growth_hack/game.html')
                return HttpResponse(template.render(context, request))

        elif GameVoucher.objects.filter(customer=customer).count() == 1:

            game_voucher = GameVoucher.objects.get(customer=customer)

            title = str(customer.first_name + ", vous avez gagné " + str(game_voucher.voucher_value) + "€ chez " + game_voucher.merchant.name + " !")

            text = str(
                "Bon d'achat de " + str(game_voucher.voucher_value) + "€ valable 7 jours pour toute commande supérieure à 20€ avec le code : " + game_voucher.voucher_code + " 😍")

            context = {
                'title': title,
                'text': text,
                'merchant_id': game_voucher.merchant.mw_offer_id,
            }
            template = loader.get_template('please_marketing_growth_hack/game.html')
            return HttpResponse(template.render(context, request))


def send_email_voucher(email, neighborhood, context):
    try:
        Lead(
            email=email,
            first_name='' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[0].capitalize(),
            last_name='' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[1].capitalize(),
        ).save()

        update_intercom_user(
            email=email,
            first_name='',
            last_name='',
            phone='',
            neighborhood=neighborhood,
            street='',
            city='',
            zip='',
            longitude='',
            latitude='',
            marketing='',
            sign_up_date=''
        )

        track_event(
            email=email,
            event_name='Completed Voucher Form Vernon',
            metadata={}
        )

        msg = EmailMessage(
            str("🎁 Votre cadeau !"),
            str(render_to_string('please_marketing_growth_hack/email_templates/email_voucher_vernon',
                                 context)),
            "Please <contact@pleaseapp.com>",
            [email],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        print("SUCCESS: Voucher Form Vernon Landing Page Email properly sent to user " + email)

    except:
        try:
            Lead(
                email=email,
                first_name='' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[
                    0].capitalize(),
                last_name='' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[
                    1].capitalize(),
            ).save()

            update_intercom_user(
                email=email,
                first_name='',
                last_name='',
                phone='',
                neighborhood=neighborhood,
                street='',
                city='',
                zip='',
                longitude='',
                latitude='',
                marketing='',
                sign_up_date=''
            )

            track_event(
                email=email,
                event_name='Completed Voucher Form Vernon',
                metadata={}
            )

            msg = EmailMessage(
                str("🎁 Votre cadeau !"),
                str(render_to_string('please_marketing_growth_hack/email_templates/email_voucher_vernon',
                                     context)),
                "Please <contact@pleaseapp.com>",
                [email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            print("SUCCESS: Voucher Form Vernon Landing Page Email properly sent to user " + email)
        except:
            print("ERROR: Voucher Form Vernon Landing Page Email not sent to user " + email + " - " + str(sys.exc_info()))
    return


def game_vernon_email(email_input):

    def coin_game(email, merchant, voucher_amount):

        voucher_amount_txt = str(str(voucher_amount) + "€")

        voucher_code = get_one_voucher_options(
            customer_id='',
            minimum_cart_amount=20,
            first_customer_order=False,
            first_order_only=True,
            voucher_val_type='amount',
            voucher_value=voucher_amount,
            voucher_validity=7,
            voucher_name=str("Coupon Jeu Tirage au Sort Vernon - " + str(email)),
            notification_type="Coupon Jeu Tirage au Sort Vernon",
            pricelist_id=merchant.odoo_offer_id,
            voucher_code=0
        )[0]

        title = str("Vous avez gagné " + voucher_amount_txt + " chez " + merchant.name + " !")

        text = str("Bon d'achat de " + voucher_amount_txt + " valable 7 jours pour toute commande supérieure à 20€ avec le code : " + voucher_code + " 😍")

        GameVoucherVernon(
            email=email,
            voucher_code=voucher_code,
            merchant=merchant,
            voucher_value=10,
        ).save()

        context_output = {
            'title': title,
            'text': text,
            'merchant_id': merchant.mw_offer_id,
        }

        return context_output

    neighborhood = Neighborhood.objects.get(mw_id=155)
    merchant_target = Merchant.objects.filter(neighborhood=neighborhood, odoo_offer_id__isnull=False, active=True).order_by("?").first()
    coin = random.randint(1, 4)

    if GameVoucherVernon.objects.filter(email=email_input).count() == 0:

        if coin == 1:
            def send_gift():
                context = coin_game(email=email_input, voucher_amount=10, merchant=merchant_target)
                send_email_voucher(email=email_input, neighborhood=neighborhood, context=context)
                return

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(send_gift, timeout=30)

        elif coin == 2:
            def send_gift():
                context = coin_game(email=email_input, voucher_amount=7, merchant=merchant_target)
                send_email_voucher(email=email_input, neighborhood=neighborhood, context=context)
                return

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(send_gift, timeout=30)

        elif coin == 3:
            def send_gift():
                context = coin_game(email=email_input, voucher_amount=5, merchant=merchant_target)
                send_email_voucher(email=email_input, neighborhood=neighborhood, context=context)
                return

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(send_gift, timeout=30)

        elif coin == 4:
            def send_gift():
                context = coin_game(email=email_input, voucher_amount=3, merchant=merchant_target)
                send_email_voucher(email=email_input, neighborhood=neighborhood, context=context)
                return

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(send_gift, timeout=30)

    return


def game_vernon(request):

    if request.method == 'POST':
        form_sign_up = GameVoucherVernonForm(data=request.POST)

        if form_sign_up.is_valid():
            email = form_sign_up.cleaned_data["email"]
            game_vernon_email(email_input=email)

            return redirect('/jeux/merci_vernon')

        else:
            context = {}

            template = loader.get_template('please_marketing_growth_hack/invalid_form.html')
            return HttpResponse(template.render(context, request))

    else:

        context = {
            "form_sign_up": GameVoucherVernonForm(),
        }

        template = loader.get_template('please_marketing_growth_hack/game_vernon_inscription.html')
        return HttpResponse(template.render(context, request))


def game_vernon_merci(request):

    context = {
        "form_sign_up": GameVoucherVernonForm(),
    }

    template = loader.get_template('please_marketing_growth_hack/game_vernon_merci.html')
    return HttpResponse(template.render(context, request))