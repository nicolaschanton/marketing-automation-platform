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
from please_marketing_app.models import Neighborhood, Customer, Merchant, VoucherCode
from please_marketing_landing_pages.models import Lead, LandingPageImage, LandingPageText
from please_marketing_landing_pages.forms import SignUpFormFull, VoucherForm, GameForm
from please_marketing_app.get_vouchers.get_voucher_landing_pages import get_one_voucher
from please_marketing_app.main_scripts.utilities import is_mobile
import requests
from rq import Queue
from worker_urgent_tasks import conn_urgent_tasks
import random
from twilio.rest import Client
import emoji
from django.db.models import Q
from django.db.models import Count
from django.contrib.postgres import search
import sys
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from please_marketing_pictures.models import MerchantPictureSource
from django.conf import settings
import cloudinary
from please_marketing_landing_pages.sign_up_please import sign_up_lead, update_intercom_user, track_event


# from please_marketing_landing_pages.views import *
# URL PARAMETERS FOR THIS PAGE = nbid, txt_name, img_name, search_term
def get_featured_merchants(raw_search_terms, neighborhood):
    base_featured_merchants = Merchant.objects.filter(
        neighborhood=neighborhood,
        active=True,
        picture_raw__isnull=False,
    ).exclude(rating__lt=3.5).order_by("-rating_number", "rating")

    if raw_search_terms:

        # Case DEFAULT
        if raw_search_terms == "default":
            featured_merchants = base_featured_merchants.filter(
                universe_name__icontains="restaurant"
            )[:4]

        # Case FAST FOOD
        elif raw_search_terms == "fastfood" or raw_search_terms == "fast food":
            featured_merchants = base_featured_merchants.filter(
                Q(universe_name__icontains="fast food") | Q(universe_name__icontains="fastfood")
            )[:4]

        # Case SIMPLE SEARCH TERM
        elif len(raw_search_terms.split(" ")) == 1:
            term = raw_search_terms
            featured_merchants = base_featured_merchants.filter(
                Q(name__icontains=term) | Q(tags__icontains=term)
            ).order_by("-rating_number", "rating")[:4]

            counter = featured_merchants.count()

            if counter > 0:
                featured_merchants = featured_merchants

            else:
                featured_merchants = base_featured_merchants.filter(
                    universe_name__icontains="restaurant"
                )[:4]

        # Case MULTIPLE SEARCH TERMS
        elif len(raw_search_terms.split(" ")) > 1:
            terms = raw_search_terms.split(" ")
            featured_merchants = Merchant.objects.none()

            for term in terms:
                featured_merchants = featured_merchants.union(
                    base_featured_merchants.filter(
                        Q(name__icontains=term) | Q(tags__icontains=term)
                    )
                )

            if featured_merchants.count() >= 4:
                featured_merchants = featured_merchants[:4]

            elif featured_merchants.count() > 0:
                featured_merchants = featured_merchants

            else:
                featured_merchants = base_featured_merchants.filter(
                    universe_name__icontains="restaurant"
                )[:4]

        # Case n°4 WARNING
        else:
            featured_merchants = base_featured_merchants.filter(
                universe_name__icontains="restaurant"
            )[:4]

    else:
        featured_merchants = base_featured_merchants.filter(
            universe_name__icontains="restaurant"
        )[:4]

    return featured_merchants


def get_voucher_alert():

    voucher_code = get_one_voucher(
        voucher_name=str("Coupon Première Commande - Campagne AdWords"),
        voucher_validity=15,
        voucher_value=5,
        voucher_val_type='amount',
        voucher_code=0,
        first_order_only=True,
        first_customer_order=True,
        minimum_cart_amount=20,
        maximum_cart_amount='',
        odoo_customer_id='',
    )[0]

    return voucher_code


def send_email_voucher(email, neighborhood, img_name, txt_name, search_term):
    try:
        Lead(
            email=email,
            first_name='' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[0].capitalize(),
            last_name='' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[1].capitalize(),
            neighborhood=neighborhood,
            img_name=img_name,
            txt_name=txt_name,
            search_term=search_term,
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
            event_name='Completed Voucher Alert Form',
            metadata={}
        )

        msg = EmailMessage(
            str("🎁 Votre bon de 5€ !"),
            str(render_to_string('please_marketing_landing_pages/email_templates/email_voucher_alert',
                                 {'voucher_code': get_voucher_alert()})),
            "Please <contact@pleaseapp.com>",
            [email],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        print("SUCCESS: Voucher Alert Landing Page Email properly sent to user " + email)

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
                neighborhood='',
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
                event_name='Completed Voucher Alert Form',
                metadata={}
            )

            msg = EmailMessage(
                str("🎁 Votre bon de 5€ !"),
                str(render_to_string('please_marketing_landing_pages/email_templates/email_voucher_alert',
                                     {'voucher_code': get_voucher_alert()})),
                "Please <contact@pleaseapp.com>",
                [email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            print("SUCCESS: Voucher Alert Landing Page Email properly sent to user " + email)
        except:
            print("ERROR: Voucher Alert Landing Page Email not sent to user " + email + " - " + str(sys.exc_info()))
    return


# PAGE VIEWS
def lp_alert(request):
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    neighborhood = Neighborhood.objects.filter().order_by("?").first() if not Neighborhood.objects.filter(mw_id=request.GET.get('nbid')) else Neighborhood.objects.filter(mw_id=int(request.GET.get('nbid'))).first()

    url_parameters = str('nbid=' + str(request.GET.get('nbid')) + '&txt_name=' + str(request.GET.get('txt_name')) + '&img_name=' + str(request.GET.get('img_name')) + '&search_term=' + str(request.GET.get('search_term')))

    if request.method == 'POST':
        form_voucher = VoucherForm(data=request.POST)
        if form_voucher.is_valid():
            email = form_voucher.cleaned_data["email"]

            # GET URL PARAMETERS
            img_name = '' if not request.GET.get('img_name') else request.GET.get('img_name')
            txt_name = '' if not request.GET.get('txt_name') else request.GET.get('txt_name')
            search_term = '' if not request.GET.get('search_term') else request.GET.get('search_term')

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(send_email_voucher, args=[
                email,
                neighborhood,
                img_name,
                txt_name,
                search_term
            ], timeout=15)

            return redirect('/ads/lpad?' + url_parameters + "&email=" + str(email))

    page_name = 'lpa'

    merchant_list = Merchant.objects.filter(neighborhood=neighborhood, active=True).order_by("-universe_name", "-rating").exclude(picture_raw='').exclude(picture_raw__isnull=True)

    featured_merchants = get_featured_merchants(
        raw_search_terms=request.GET.get('search_term'),
        neighborhood=neighborhood
    )

    header_image = LandingPageImage.objects.filter(image_type='hr', target_page=page_name).order_by('?').first() if not LandingPageImage.objects.filter(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name) else LandingPageImage.objects.get(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name)

    header_text = LandingPageText.objects.filter(text_type='hr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name)

    sub_header_text = LandingPageText.objects.filter(text_type='sr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name)

    context = {
        "neighborhood": neighborhood,
        "featured_merchants": featured_merchants,
        "merchant_list": merchant_list,
        "header_image_url": header_image.image_file.build_url(
            transformation=[
                {
                    'width': 800 if is_mobile(http_request=request) else 2200,
                    'crop': "scale",
                    "format": "jpg"
                }
            ]
        ).replace("http://", "https://"),
        "header_text": header_text,
        "sub_header_text": sub_header_text,
        "voucher_form": VoucherForm(),
        "url_parameters": url_parameters,
        "RESPONSIVE_EFFECTS": dict(
          format="jpg",
          transformation=[
              dict(width="auto", crop="scale", quality=60),
          ]
        )
    }

    template = loader.get_template('please_marketing_landing_pages/lp_alert.html')
    response = HttpResponse(template.render(context, request))
    response['Cache-Control'] = 'max-age=86400'
    return response


def lp_alert_done(request):
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    email = str('' if not request.GET.get('email') else request.GET.get('email'))
    first_name = str('' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[0].capitalize())
    last_name = str('' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[1].capitalize())

    url_parameters = str('nbid=' + str(request.GET.get('nbid')) + '&txt_name=' + str(request.GET.get('txt_name')) + '&img_name=' + str(request.GET.get('img_name')) + '&email=' + email + '&first_name=' + first_name + '&last_name=' + last_name + '&search_term=' + str(request.GET.get('search_term')))

    page_name = 'lpad'

    neighborhood = Neighborhood.objects.filter().order_by("?").first() if not Neighborhood.objects.filter(mw_id=request.GET.get('nbid')) else Neighborhood.objects.filter(mw_id=int(request.GET.get('nbid'))).first()

    merchant_list = Merchant.objects.filter(neighborhood=neighborhood, active=True).order_by("-universe_name", "-rating").exclude(picture_raw='').exclude(picture_raw__isnull=True)

    featured_merchants = get_featured_merchants(
        raw_search_terms=request.GET.get('search_term'),
        neighborhood=neighborhood
    )

    header_image = LandingPageImage.objects.filter(image_type='hr', target_page=page_name).order_by('?').first() if not LandingPageImage.objects.filter(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name) else LandingPageImage.objects.get(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name)

    header_text = LandingPageText.objects.filter(text_type='hr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name)

    sub_header_text = LandingPageText.objects.filter(text_type='sr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name)

    context = {
        "neighborhood": neighborhood,
        "featured_merchants": featured_merchants,
        "merchant_list": merchant_list,
        "header_image_url": header_image.image_file.build_url(
            transformation=[
                {
                    'width': 800 if is_mobile(http_request=request) else 2200,
                    'crop': "scale",
                    "format": "jpg"
                }
            ]
        ).replace("http://", "https://"),
        "header_text": header_text,
        "sub_header_text": sub_header_text,
        "url_parameters": url_parameters,
        "RESPONSIVE_EFFECTS": dict(
          format="jpg",
          transformation=[
              dict(width="auto", crop="scale", quality=60),
          ]
        )
    }

    template = loader.get_template('please_marketing_landing_pages/lp_alert_done.html')
    response = HttpResponse(template.render(context, request))
    response['Cache-Control'] = 'max-age=86400'
    return response


def lp_signup(request):
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    page_name = 'lps'

    neighborhood = Neighborhood.objects.filter().order_by("?").first() if not Neighborhood.objects.filter(mw_id=request.GET.get('nbid')) else Neighborhood.objects.filter(mw_id=int(request.GET.get('nbid'))).first()

    email = str('' if not request.GET.get('email') else request.GET.get('email'))
    first_name = str('' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[0].capitalize())
    last_name = str('' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[1].capitalize())

    url_parameters = str('nbid=' + str(request.GET.get('nbid')) + '&txt_name=' + str(request.GET.get('txt_name')) + '&img_name=' + str(request.GET.get('img_name')) + '&email=' + email + '&first_name=' + first_name + '&last_name=' + last_name + '&search_term=' + str(request.GET.get('search_term')))

    if request.method == 'POST':
        sign_up_form = SignUpFormFull(data=request.POST)
        if sign_up_form.is_valid():
            email = sign_up_form.cleaned_data["email"]
            password = sign_up_form.cleaned_data["password"]
            first_name = sign_up_form.cleaned_data["first_name"]
            last_name = sign_up_form.cleaned_data["last_name"]
            country_code = sign_up_form.cleaned_data["country_code"]
            phone_raw = sign_up_form.cleaned_data["phone"]
            address_raw = sign_up_form.cleaned_data["address"]

            phone = str(country_code + phone_raw.lstrip("0"))

            marketing = True if sign_up_form.cleaned_data["marketing"] == "True" else False

            # GET URL PARAMETERS
            img_name = '' if not request.GET.get('img_name') else request.GET.get('img_name')
            txt_name = '' if not request.GET.get('txt_name') else request.GET.get('txt_name')
            search_term = '' if not request.GET.get('search_term') else request.GET.get('search_term')

            q_urgent_tasks = Queue(connection=conn_urgent_tasks)
            q_urgent_tasks.enqueue(sign_up_lead,
                                   args=(
                                       email,
                                       password,
                                       first_name,
                                       last_name,
                                       phone,
                                       address_raw,
                                       neighborhood,
                                       img_name,
                                       txt_name,
                                       search_term,
                                       marketing
                                   ),
                                   timeout=30)

            return redirect('/ads/merci?' + url_parameters)

    header_image = LandingPageImage.objects.filter(image_type='hr', target_page=page_name).order_by('?').first() if not LandingPageImage.objects.filter(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name) else LandingPageImage.objects.get(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name)

    header_text = LandingPageText.objects.filter(text_type='hr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name)

    sub_header_text = LandingPageText.objects.filter(text_type='sr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name)

    context = {
        "neighborhood": neighborhood,
        "header_image_url": header_image.image_file.build_url(
            transformation=[
                {
                    'width': 800 if is_mobile(http_request=request) else 2200,
                    'crop': "scale",
                    "format": "jpg"
                }
            ]
        ).replace("http://", "https://"),
        "header_text": header_text,
        "sub_header_text": sub_header_text,
        "sign_up_form": SignUpFormFull(),
        "url_parameters": url_parameters,
    }

    template = loader.get_template('please_marketing_landing_pages/lp_signup.html')
    response = HttpResponse(template.render(context, request))
    response['Cache-Control'] = 'max-age=86400'
    return response


def thanks(request):
    neighborhood = Neighborhood.objects.filter().order_by("?").first() if not Neighborhood.objects.filter(mw_id=request.GET.get('nbid')) else Neighborhood.objects.filter(mw_id=int(request.GET.get('nbid'))).first()

    email = str('' if not request.GET.get('email') else request.GET.get('email'))
    first_name = str('' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[0].capitalize())
    last_name = str('' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[1].capitalize())

    url_parameters = str('nbid=' + str(request.GET.get('nbid')) + '&txt_name=' + str(request.GET.get('txt_name')) + '&img_name=' + str(request.GET.get('img_name')) + '&email=' + email + '&first_name=' + first_name + '&last_name=' + last_name + '&search_term=' + str(request.GET.get('search_term')))

    context = {
        'nbid': neighborhood.mw_id,
        'txt_name': "default" if not request.GET.get('txt_name') else request.GET.get('txt_name'),
        'img_name': "default" if not request.GET.get('img_name') else request.GET.get('img_name'),
        'url_parameters': url_parameters,

    }
    template = loader.get_template('please_marketing_landing_pages/thanks.html')
    response = HttpResponse(template.render(context, request))
    response['Cache-Control'] = 'max-age=86400'
    return response


def lp(request):
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    email = str('' if not request.GET.get('email') else request.GET.get('email'))
    first_name = str('' if len(email.split("@")[0].split(".")) == 0 else email.split("@")[0].split(".")[0].capitalize())
    last_name = str('' if len(email.split("@")[0].split(".")) is not 2 else email.split("@")[0].split(".")[1].capitalize())

    url_parameters = str('nbid=' + str(request.GET.get('nbid')) + '&txt_name=' + str(request.GET.get('txt_name')) + '&img_name=' + str(request.GET.get('img_name')) + '&email=' + email + '&first_name=' + first_name + '&last_name=' + last_name + '&search_term=' + str(request.GET.get('search_term')))

    page_name = 'lp'

    neighborhood = Neighborhood.objects.filter().order_by("?").first() if not Neighborhood.objects.filter(mw_id=request.GET.get('nbid')) else Neighborhood.objects.filter(mw_id=int(request.GET.get('nbid'))).first()

    merchant_list = Merchant.objects.filter(neighborhood=neighborhood, active=True).order_by("-universe_name", "-rating").exclude(picture_raw='').exclude(picture_raw__isnull=True)

    featured_merchants = get_featured_merchants(
        raw_search_terms=request.GET.get('search_term'),
        neighborhood=neighborhood
    )

    header_image = LandingPageImage.objects.filter(image_type='hr', target_page=page_name).order_by('?').first() if not LandingPageImage.objects.filter(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name) else LandingPageImage.objects.get(image_type='hr', image_name=request.GET.get('img_name'), target_page=page_name)

    header_text = LandingPageText.objects.filter(text_type='hr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='hr', text_name=request.GET.get('txt_name'), target_page=page_name)

    sub_header_text = LandingPageText.objects.filter(text_type='sr', target_page=page_name).order_by('?').first() if not LandingPageText.objects.filter(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name) else LandingPageText.objects.get(text_type='sr', text_name=request.GET.get('txt_name'), target_page=page_name)

    context = {
        "neighborhood": neighborhood,
        "featured_merchants": featured_merchants,
        "merchant_list": merchant_list,
        "header_image_url": header_image.image_file.build_url(
            transformation=[
                {
                    'width': 800 if is_mobile(http_request=request) else 2200,
                    'crop': "scale",
                    "format": "jpg"
                }
            ]
        ).replace("http://", "https://"),
        "header_text": header_text,
        "sub_header_text": sub_header_text,
        "url_parameters": url_parameters,
        "RESPONSIVE_EFFECTS": dict(
          format="jpg",
          transformation=[
              dict(
                  width="auto",
                  crop="scale",
                  quality=60
              ),
          ]
        )
    }

    template = loader.get_template('please_marketing_landing_pages/lp.html')
    response = HttpResponse(template.render(context, request))
    response['Cache-Control'] = 'max-age=86400'
    return response


def redirect_to_store_ranking(request):
    # ip_address = request.META.get('REMOTE_ADDR')
    # log_name = request.META.get('LOGNAME')
    user_agent = request.META.get('HTTP_USER_AGENT').lower()
    # referral_domain = request.META.get('HTTP_REFERER')

    print(user_agent)

    if "android" in user_agent:
        return redirect('https://play.google.com/store/apps/details?id=com.pleaseit.please')

    elif ("iphone" or "ipad") in user_agent:
        return redirect('https://itunes.apple.com/fr/app/please-mon-home-service/id1130427303?mt=8')

    else:
        print(user_agent)
        return redirect('https://pleaseapp.com')


def please_game_play(request, sharable_id):

    # CLOUDINARY CONFIGURATION
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    # CUSTOMER RECOGNITION
    customer = Customer.objects.filter(sharable_user_id=sharable_id).first()

    if customer and (not customer.birth_date or not customer.favourite_dish):
        header_image = LandingPageImage.objects.filter(image_name="please_game").first()

        if request.method == 'POST':
            form = GameForm(data=request.POST)
            if form.is_valid():
                birth_date = form.cleaned_data["birth_date"]
                favourite_dish = form.cleaned_data["favourite_dish"]

                customer.birth_date = birth_date
                customer.favourite_dish = favourite_dish
                customer.save()

                return redirect("/ads/game/" + str(customer.sharable_user_id))

        context = {
            "form": GameForm(),
            "header_image_url": header_image.image_file.build_url(
                transformation=[
                    {
                        'width': 800 if is_mobile(http_request=request) else 2200,
                        'crop': "scale",
                        "format": "jpg"
                    }
                ]
            ).replace("http://", "https://")
        }

        template = loader.get_template('please_marketing_landing_pages/game_play.html')
        response = HttpResponse(template.render(context, request))
        response['Cache-Control'] = 'max-age=86400'
        return response

    else:
        return redirect("https://pleaseapp.com")


def please_game(request, sharable_id):

    # CLOUDINARY CONFIGURATION
    cloudinary.config(
        cloud_name=str(settings.CLOUDINARY_CLOUD_NAME),
        api_key=str(settings.CLOUDINARY_API_KEY),
        api_secret=str(settings.CLOUDINARY_API_SECRET)
    )

    # CUSTOMER RECOGNITION
    customer = Customer.objects.filter(sharable_user_id=sharable_id).first()
    voucher_code = VoucherCode.objects.filter(customer=customer, name__icontains="Please Game 2019").first()

    if customer and customer.birth_date and customer.favourite_dish and not voucher_code:
        header_image = LandingPageImage.objects.filter(image_name="please_game").first()

        coin = random.randint(1, 10)
        print(coin)

        if coin == 1:
            voucher_code_new = get_one_voucher(
                voucher_name="Please Game 2019",
                voucher_validity=7,
                voucher_value=5,
                voucher_val_type="amount",
                voucher_code=0,
                first_order_only=True,
                first_customer_order=False,
                minimum_cart_amount=20,
                maximum_cart_amount="",
                odoo_customer_id=int(customer.odoo_user_id),
            )[0]

            voucher_code_new = VoucherCode(
                customer=customer,
                code=str(voucher_code_new),
                name="Please Game 2019",
                voucher_type="Please Game",
                value=5,
                expiry_date=datetime.datetime.now(),
                notification_type="Web",
            )
            voucher_code_new.save()

            result = str("Vous avez gagné 5€ (valable 7j) avec le code " + str(voucher_code_new))

        else:
            voucher_code_new = VoucherCode(
                customer=customer,
                code="0000",
                name="Please Game 2019",
                voucher_type="Please Game",
                value=0,
                expiry_date=datetime.datetime.now(),
                notification_type="Web",
            )
            voucher_code_new.save()
            result = str(
                str("Vous avez perdu ")
                + str(emoji.emojize(u':pensive:', use_aliases=True))
                + str(" !")
            )

        context = {
            "result": result,
            "header_image_url": header_image.image_file.build_url(
                transformation=[
                    {
                        "crop": "scale",
                        "format": "jpg",
                    }
                ]
            ).replace("http://", "https://")
        }

        template = loader.get_template('please_marketing_landing_pages/game.html')
        response = HttpResponse(template.render(context, request))
        response['Cache-Control'] = 'max-age=86400'
        return response

    else:
        return redirect("https://pleaseapp.com")


def unsubscribe(request):
    sharable_user_id = str('' if not request.GET.get('customer') else request.GET.get('customer'))

    context = {}

    # Updating Customer Subscription Preferences
    if sharable_user_id:
        if Customer.objects.filter(sharable_user_id=sharable_user_id).count() == 1:
            customer = Customer.objects.filter(sharable_user_id=sharable_user_id).first()
            customer.unsubscribed_from_emails = True
            customer.save()

            # Create Event
            track_event(
                email=customer.email,
                event_name="unsubscribed from email",
                metadata={}
            )

    template = loader.get_template('please_marketing_landing_pages/unsubscribe.html')
    response = HttpResponse(template.render(context, request))
    response['Cache-Control'] = 'max-age=86400'
    return response
