from django.shortcuts import render
import json
from .recommendation_system_2 import get_recommendation
from please_marketing_app.models import Customer
from please_marketing_extra_user_enrichment.models import AddressEnrichmentSl
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


def ae(request):
    secret = "" if not request.GET.get("secret_key") else request.GET.get("secret_key")
    email = "" if not request.GET.get("email") else request.GET.get("email")

    if secret == str(settings.PLEASE_MARKET_SECRET):
        if email:
            aer = AddressEnrichmentSl.objects.filter().first(email)
            resp = []
            for r in aer:
                re = {
                    "customer": r.customer.id,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "label": r.label,
                    "cp": r.cp,
                    "summary_prices_max": r.summary_prices_max,
                    "summary_prices_med": r.summary_prices_med,
                    "summary_prices_min": r.summary_prices_min,
                    "market_numbers_selling": r.market_numbers_selling,
                    "market_numbers_sold": r.market_numbers_sold,
                    "market_numbers_numberMainResidence": r.market_numbers_numberMainResidence,
                    "market_numbers_numberSecondaryResidence": r.market_numbers_numberSecondaryResidence,
                    "market_numbers_numberTotalResidence": r.market_numbers_numberTotalResidence,
                    "single": r.single,
                    "couple": r.couple,
                    "family": r.family,
                    "poi_transport_count": r.poi_transport_count,
                    "poi_education_count": r.poi_education_count,
                    "poi_neighbors_count": r.poi_neighbors_count,
                    "poi_hotels_count": r.poi_hotels_count,
                    "poi_commerces_count": r.poi_commerces_count,
                    "nbLogements": r.nbLogements,
                    "nbHabitants": r.nbHabitants,
                    "peopleDensity": r.peopleDensity,
                    "ageMed": r.ageMed,
                    "age25MoinsPcent": r.age25MoinsPcent,
                    "age25PlusPcent": r.age25PlusPcent,
                    "nbEntreprises": r.nbEntreprises,
                    "nbCreationEntreprises": r.nbCreationEntreprises,
                    "pcentActifsAll": r.pcentActifsAll,
                    "pcentActifs30": r.pcentActifs30,
                    "pcentUnemployed": r.pcentUnemployed,
                    "averageIncome": r.averageIncome,
                    "pcentEtudiants": r.pcentEtudiants,
                    "pcentResPrincipales": r.pcentResPrincipales,
                    "pcentResSecondaires": r.pcentResSecondaires,
                    "pcentLogVacants": r.pcentLogVacants,
                    "pcentLocataires": r.pcentLocataires,
                    "pcentPrpriotaires": r.pcentPrpriotaires,
                    "pcentAppartement": r.pcentAppartement,
                    "pcentMaisons": r.pcentMaisons,
                }

                resp.append(re)

            return HttpResponse(
                            json.dumps(resp),
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