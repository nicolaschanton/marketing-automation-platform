# coding: utf-8

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template import loader
import copy, json, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .main_scripts.intercom import receive_intercom_events, executor_save_intercom_events_30
from .main_scripts.nps import send_voucher_nps
from .main_scripts.activate_rookies import activate_rookie_amount, activate_rookie_percent
import hashlib
import hmac
from .models import Customer, Order, NetPromoterScore, IntercomEvent, Customer, Fete, Merchant, SmsHistory, DeliveryManLead, Neighborhood
from rq import Queue
from worker_urgent_tasks import conn_urgent_tasks
from worker_tracking_events import conn_tracking_events
from worker_background_tasks import conn_background_tasks
import random
from twilio.rest import Client
from datetime import datetime
from django.conf import settings
from django.db.models import Q
import sys
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

q_urgent_tasks = Queue('high', connection=conn_urgent_tasks)
q_tracking_events = Queue('high', connection=conn_tracking_events)
q_background_tasks = Queue('high', connection=conn_background_tasks)


def index(request):
    return HttpResponseRedirect("/admin/")


@csrf_exempt
@require_POST
def trigger_ie_30(request):

    json_data = json.loads(request.body)

    if json_data.get("user_id") == "please_marketing" and json_data.get("password") == "A$t(ty§7lzl@éz>ù09G<":

        q_background_tasks.enqueue(executor_save_intercom_events_30, args=[], timeout=84000)

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def webhook_intercom_events(request):

    json_data = json.loads(request.body)
    event_data = json_data.get("data").get("item")

    if Customer.objects.filter(email=event_data.get("email")).count() == 1:
        q_tracking_events.enqueue(receive_intercom_events, args=[event_data], timeout=200)

        # Trigger for Activation Rookie SMS
        if event_data.get("event_name") == "viewed offer":
            customer = Customer.objects.get(email=event_data.get("email"))

            q_urgent_tasks.enqueue(activate_rookie_amount, args=[customer], timeout=200)

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def webhook_nps(request):

    json_data = json.loads(request.body)

    print(json_data)
    if (json_data.get("form_response").get("hidden").get("id") is not None) and (json_data.get("form_response").get("hidden").get("id") is not ''):
        if Customer.objects.filter(id=json_data.get("form_response").get("hidden").get("id")).count() == 1:
            customer = Customer.objects.get(id=json_data.get("form_response").get("hidden").get("id"))
            if NetPromoterScore.objects.filter(customer=customer).count() == 0:
                NetPromoterScore(
                    customer=customer,
                    score=int(json_data.get("form_response").get("answers")[0].get("number")),
                    description=None if not json_data.get("form_response").get("answers")[1].get("text") else json_data.get("form_response").get("answers")[1].get("text")
                ).save()

                send_voucher_nps(customer=customer, score=int(json_data.get("form_response").get("answers")[0].get("number")))

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def delivery_men_leads(request):

    json_data = json.loads(request.body)

    print(json_data)

    if (json_data.get("event_type") == "form_response") and (json_data.get("form_response").get("definition").get("id") == "hODi4j"):

        if DeliveryManLead.objects.filter(email=json_data.get("form_response").get("answers")[3].get("text")).count() == 0:

            DeliveryManLead(
                email=json_data.get("form_response").get("answers")[3].get("text"),
                first_name=json_data.get("form_response").get("answers")[0].get("text"),
                last_name=json_data.get("form_response").get("answers")[1].get("text"),
                phone=json_data.get("form_response").get("answers")[4].get("text"),
                city=json_data.get("form_response").get("answers")[2].get("text"),
            ).save()

    return HttpResponse(status=200)


def get_neighborhood_open(request, mw_nbid):
    neighborhood = Neighborhood.objects.filter(mw_id=mw_nbid).first()
    if neighborhood:
        data = {
            "is_open": neighborhood.is_open,
            "open_date": neighborhood.open_date,
        }
    else:
        data = {
            "message": "Neighborhood not found"
        }

    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = "*"
    return response
