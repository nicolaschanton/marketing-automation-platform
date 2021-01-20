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
from please_marketing_app.models import Customer, Order, NetPromoterScore, IntercomEvent, Customer, Fete, Merchant, SmsHistory
from .models import ReferralLead, ReferralMatch
from .forms import SendEmailReferralForm, SendSmsReferralForm, LoginForm
import random
from twilio.rest import Client
from datetime import datetime
from django.conf import settings
from django.db.models import Q
import sys
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rq import Queue
from worker_mid_urgent_tasks import conn_mid_urgent_tasks
from .referral_sender import send_email_referral, send_sms_referral
from.intercom_tracking import track_event
from .utilities import get_client_ip

q_mid_urgent_tasks = Queue(connection=conn_mid_urgent_tasks)


def referral(request):
    referral_code = request.GET.get('r', '')

    if referral_code == "NO_USER":
        return redirect("http://onelink.to/pleaseapp")

    else:
        referrer = Customer.objects.get(referral_code=referral_code)
        latest_booking = str("de votre ville") if not Order.objects.filter(customer=referrer, odoo_order_state='done', universe_name__in=["Restaurants", "Fast Food", "Petit-déjeuners et pâtisseries"]).order_by("-order_date").first() else str("de " + Order.objects.filter(customer=referrer, odoo_order_state='done', universe_name__in=["Restaurants", "Fast Food", "Petit-déjeuners et pâtisseries"]).order_by("-order_date").first().offer_name)

        track_event(
            event_name="viewed referral page",
            customer=referrer,
            metadata={
                "user_agent_data": str(request.META['HTTP_USER_AGENT']),
                "language": "French (France)",
                "from": "website",
                "ip_address": str(get_client_ip(request=request)),
            }
        )

        if request.method == 'POST':
            form_sms = SendSmsReferralForm(data=request.POST)
            form_email = SendEmailReferralForm(data=request.POST)
            if form_sms.is_valid():
                phone = form_sms.cleaned_data["phone"]
                country_code = referrer.phone[:-9]
                formatted_phone = str(str(country_code) + phone.lstrip("0"))

                q_mid_urgent_tasks.enqueue(send_sms_referral, args=[formatted_phone, referrer], timeout=60)
                return redirect('/parrainage/parrainage_sms?r=' + referrer.referral_code)
            elif form_email.is_valid():
                email = form_email.cleaned_data["email"]
                q_mid_urgent_tasks.enqueue(send_email_referral, args=[email, referrer, latest_booking], timeout=60)
                return redirect('/parrainage/parrainage_email?r=' + referrer.referral_code)

        else:
            context = {
                "customer": referrer,
                "form_referral_email": SendEmailReferralForm(),
                "form_referral_sms": SendSmsReferralForm(),
            }

            template = loader.get_template('please_marketing_referral_program/parrainage.html')
            return HttpResponse(template.render(context, request))


def referral_sms(request):
    referral_code = request.GET.get('r', '')
    referrer = Customer.objects.get(referral_code=referral_code)
    latest_booking = str("de votre ville") if not Order.objects.filter(customer=referrer, odoo_order_state='done',
                                                                         universe_name__in=["Restaurants", "Fast Food",
                                                                                            "Petit-déjeuners et pâtisseries"]).order_by(
        "-order_date").first() else str("de " + Order.objects.filter(customer=referrer, odoo_order_state='done',
                                                                     universe_name__in=["Restaurants", "Fast Food",
                                                                                        "Petit-déjeuners et pâtisseries"]).order_by(
        "-order_date").first().offer_name)

    if request.method == 'POST':
        form_sms = SendSmsReferralForm(data=request.POST)
        form_email = SendEmailReferralForm(data=request.POST)
        if form_sms.is_valid():
            phone = form_sms.cleaned_data["phone"]
            country_code = referrer.phone[:-9]
            formatted_phone = str(str(country_code) + phone.lstrip("0"))

            q_mid_urgent_tasks.enqueue(send_sms_referral, args=[formatted_phone, referrer], timeout=60)
            return redirect('/parrainage/parrainage_sms?r=' + referrer.referral_code)
        elif form_email.is_valid():
            email = form_email.cleaned_data["email"]
            q_mid_urgent_tasks.enqueue(send_email_referral, args=[email, referrer, latest_booking], timeout=60)
            return redirect('/parrainage/parrainage_email?r=' + referrer.referral_code)

    else:
        context = {
            "customer": referrer,
            "form_referral_email": SendEmailReferralForm(),
            "form_referral_sms": SendSmsReferralForm(),
        }

        template = loader.get_template('please_marketing_referral_program/parrainage_sms.html')
        return HttpResponse(template.render(context, request))


def referral_email(request):
    referral_code = request.GET.get('r', '')
    referrer = Customer.objects.get(referral_code=referral_code)
    latest_booking = str("de votre ville") if not Order.objects.filter(customer=referrer, odoo_order_state='done',
                                                                         universe_name__in=["Restaurants", "Fast Food",
                                                                                            "Petit-déjeuners et pâtisseries"]).order_by(
        "-order_date").first() else str("de " + Order.objects.filter(customer=referrer, odoo_order_state='done',
                                                                     universe_name__in=["Restaurants", "Fast Food",
                                                                                        "Petit-déjeuners et pâtisseries"]).order_by(
        "-order_date").first().offer_name)

    if request.method == 'POST':
        form_sms = SendSmsReferralForm(data=request.POST)
        form_email = SendEmailReferralForm(data=request.POST)
        if form_sms.is_valid():
            phone = form_sms.cleaned_data["phone"]
            country_code = referrer.phone[:-9]
            formatted_phone = str(str(country_code) + phone.lstrip("0"))

            q_mid_urgent_tasks.enqueue(send_sms_referral, args=[formatted_phone, referrer], timeout=60)
            return redirect('/parrainage/parrainage_sms?r=' + referrer.referral_code)
        elif form_email.is_valid():
            email = form_email.cleaned_data["email"]
            q_mid_urgent_tasks.enqueue(send_email_referral, args=[email, referrer, latest_booking], timeout=60)
            return redirect('/parrainage/parrainage_email?r=' + referrer.referral_code)

    else:
        context = {
            "customer": referrer,
            "form_referral_email": SendEmailReferralForm(),
            "form_referral_sms": SendSmsReferralForm(),
        }

        template = loader.get_template('please_marketing_referral_program/parrainage_email.html')
        return HttpResponse(template.render(context, request))


def hello(request):
    referral_code = request.GET.get('r', '')
    referrer = Customer.objects.get(referral_code=referral_code)

    context = {
        "customer": referrer,
    }

    template = loader.get_template('please_marketing_referral_program/hello.html')
    return HttpResponse(template.render(context, request))


def referral_login(request):
    if request.method == 'POST':
        form_login = LoginForm(data=request.POST)

        if form_login.is_valid():
            email = form_login.cleaned_data["email"]
            customer = Customer.objects.filter(email=email).first()

            if customer:

                if customer.referral_code:
                    # q_mid_urgent_tasks.enqueue(send_sms_referral, args=[phone, referrer], timeout=60)
                    return redirect('/parrainage/parrainage?r=' + customer.referral_code)

                else:
                    context = {
                        "form_login": LoginForm(),
                    }

                    template = loader.get_template('please_marketing_referral_program/parrainage_login.html')
                    return HttpResponse(template.render(context, request))

            else:
                context = {
                    "form_login": LoginForm(),
                }

                template = loader.get_template('please_marketing_referral_program/parrainage_login.html')
                return HttpResponse(template.render(context, request))

        else:
            context = {
                "form_login": LoginForm(),
            }

            template = loader.get_template('please_marketing_referral_program/parrainage_login.html')
            return HttpResponse(template.render(context, request))

    else:
        context = {
            "form_login": LoginForm(),
        }

        template = loader.get_template('please_marketing_referral_program/parrainage_login.html')
        return HttpResponse(template.render(context, request))
