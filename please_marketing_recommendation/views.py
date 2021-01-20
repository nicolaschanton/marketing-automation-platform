from django.shortcuts import render
import json
from .recommendation_system_2 import get_recommendation
from please_marketing_app.models import Customer
from django.http import HttpResponse
from django.conf import settings


def recommendation(request):
    secret = "" if not request.GET.get("secret_key") else request.GET.get("secret_key")
    email = "" if not request.GET.get("email") else request.GET.get("email")

    if secret == str(settings.PLEASE_MARKET_SECRET):
        if email:
            if Customer.objects.filter(email=email).count() == 1:
                customer = Customer.objects.get(email=email)

                return HttpResponse(
                    json.dumps(get_recommendation(customer=customer)),
                    content_type="application/json"
                )

            else:
                return HttpResponse(
                    "No Customer Matching Query",
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                    "No Email",
                    content_type="application/json"
                )

    else:
        return HttpResponse(
                    "Not Allowed",
                    content_type="application/json"
                )
