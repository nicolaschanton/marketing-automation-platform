# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, IntercomEvent, NotificationHistory, Order, \
    NetPromoterScore, SmsHistory, Neighborhood
from .models import CosineSimilarityBooking, VectorBooking, VectorMerchant
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count
import pytz
from django.conf import settings
import requests
import json
from django.db.models import Q
import sys
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from please_marketing_script_execution.log_script import log_script
from difflib import SequenceMatcher
from operator import itemgetter
from pytz import timezone


# from please_marketing_recommendation.recommendation_system import *
# customer = Customer.objects.filter().order_by("?").first()
# print(customer, customer.neighborhood)


def is_activated(customer):
    response = True if customer.orders_number > 0 else False

    return response


def is_active(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s"))),
    ).count()

    response = True if ((customer.orders_number > 0) and (ie_count > 0)) else False

    return response


def is_frequent(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s"))),
    ).count()

    response = True if ((customer.orders_number > 4) and (ie_count > 0)) else False

    return response


def has_viewed_universe(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        event_name="viewed universe"
    ).count()

    response = True if ie_count > 0 else False

    return response


def has_viewed_offer(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        event_name="viewed offer"
    ).count()

    response = True if ie_count > 0 else False

    return response


def has_validated_basket_2(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        event_name="validated basket 2"
    ).count()

    response = True if ie_count > 0 else False

    return response


def get_best_day(day):

    if day == "Monday":
        response = "WEEK"

    elif day == "Tuesday":
        response = "WEEK"

    elif day == "Wednesday":
        response = "WEEK"

    elif day == "Thursday":
        response = "WEEK"

    elif day == "Friday":
        response = "WEEKEND"

    elif day == "Saturday":
        response = "WEEKEND"

    elif day == "Sunday":
        response = "WEEKEND"

    else:
        response = 'ISSUE'

    return response


def get_proper_datetime_tz(date_time, neighborhood):

    nb_tz = "Europe/Paris" if not neighborhood.timezone else neighborhood.timezone

    response = date_time.astimezone(timezone(str(nb_tz)))

    return response


def get_best_hour(hour):

    if 4 < int(hour) < 11:
        response = "MORNING"

    elif 11 <= int(hour) < 15:
        response = "NOON"

    else:
        response = "NIGHT"

    return response


def get_approximate_time(date, customer):

    if customer.neighborhood.mw_id == 505:
        response = date + timedelta(seconds=14400)

    else:
        response = date + timedelta(seconds=7200)

    return response


def get_clean_universe_name(raw_universe_name, customer):

    clean_universe_queryset = Order.objects.filter(
        odoo_order_state="done",
        neighborhood=customer.neighborhood,
    ).values("universe_name").distinct("universe_name")

    similiraity_tuple = []
    for clean_universe_queryset_raw in clean_universe_queryset:
        clean_universe_name = clean_universe_queryset_raw.get("universe_name")

        similiraity_tuple.append(
            (
                clean_universe_name,
                SequenceMatcher(None, raw_universe_name, clean_universe_name).ratio()
            )
        )

    result = sorted(similiraity_tuple, key=itemgetter(1), reverse=True)[0][0]

    return result


def get_device(customer):
    last_event = IntercomEvent.objects.filter(
        customer=customer,
        os_platform__isnull=False,
    ).order_by("-created_at").first()

    if last_event:
        if last_event.os_platform == "iOS":
            device = "Apple"

        elif last_event.os_platform == "Android":
            device = "Android"

        else:
            device = "Desktop"

        response = {
            "device": device
        }
        return response

    else:
        response = {
            "device": ""
        }
        return response


def get_orders(customer):

    orders_by_merchant = Order.objects.filter(
        customer=customer,
        odoo_order_state="done",
    ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")

    response_list = []
    for merchant in orders_by_merchant:

        merchant = Merchant.objects.get(mw_offer_id=merchant.get("mw_offer_id"))

        response_list.append(
            {
                "mw_offer_id": int(merchant.mw_offer_id),
                "offer_name": merchant.name,
                "mw_neighborhood_id": int(merchant.neighborhood.mw_id),
                "neighborhood_name": merchant.neighborhood.name,
                "order_counter": int(Order.objects.filter(
                    customer=customer,
                    odoo_order_state="done",
                    mw_offer_id=merchant.mw_offer_id,
                ).count()),
            }
        )

    response = {
        "customer_orders": response_list,
    }

    return response


def get_trending_merchants(customer):

    if is_active(customer=customer):
        favorite_universe = Order.objects.filter(
            customer=customer,
            odoo_order_state="done",
        ).values("universe_name").annotate(nb=Count("universe_name")).order_by("-nb").first().get("universe_name")

        trending_merchant_ids = Order.objects.filter(
            neighborhood=customer.neighborhood,
            odoo_order_state="done",
            universe_name=favorite_universe,
            order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=90)).strftime("%s"))),
        ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")[:4]

    elif has_viewed_offer(customer=customer):
        favorite_universe = IntercomEvent.objects.filter(
            customer=customer,
            event_name="viewed offer",
        ).values("universe_name").annotate(nb=Count("universe_name")).order_by("-nb").first().get("universe_name")

        favorite_universe_cleaned = get_clean_universe_name(
            raw_universe_name=favorite_universe,
            customer=customer
        )

        trending_merchant_ids = Order.objects.filter(
            neighborhood=customer.neighborhood,
            odoo_order_state="done",
            universe_name=favorite_universe_cleaned,
            order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=90)).strftime("%s"))),
        ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")[:4]

    elif has_viewed_universe(customer=customer):
        favorite_universe = IntercomEvent.objects.filter(
            customer=customer,
            event_name="viewed universe",
        ).values("universe_name").annotate(nb=Count("universe_name")).order_by("-nb").first().get("universe_name")

        favorite_universe_cleaned = get_clean_universe_name(
            raw_universe_name=favorite_universe,
            customer=customer
        )

        trending_merchant_ids = Order.objects.filter(
            neighborhood=customer.neighborhood,
            odoo_order_state="done",
            universe_name=favorite_universe_cleaned,
            order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=90)).strftime("%s"))),
        ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")[:4]

    else:
        trending_merchant_ids = Order.objects.filter(
            neighborhood=customer.neighborhood,
            odoo_order_state="done",
            order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=90)).strftime("%s"))),
        ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")[:4]

    # ANALYZE AND FORMAT TRENDING MERCHANTS LIST
    trending_merchants = []
    for m in trending_merchant_ids:
        if Merchant.objects.filter(mw_offer_id=m.get("mw_offer_id"), rating__gte=4, active=True).count() == 1:

            trending_merchant = Merchant.objects.get(
                mw_offer_id=m.get("mw_offer_id"),
                rating__gte=4,
                active=True,
            )

            trending_merchants.append(
                {
                    "mw_offer_id": int(trending_merchant.mw_offer_id),
                    "offer_name": trending_merchant.name,
                    "universe_name": trending_merchant.universe_name,
                    "mw_neighborhood_id": int(trending_merchant.neighborhood.mw_id),
                    "neighborhood_name": trending_merchant.neighborhood.name,
                    "order_count": int(Order.objects.filter(
                        mw_offer_id=trending_merchant.mw_offer_id,
                        odoo_order_state="done",
                        order_date__gt=datetime.fromtimestamp(
                            float((datetime.today() - timedelta(days=90)).strftime("%s"))
                        ),
                    ).count()),
                }
            )

    response = {
        "trending_merchants": trending_merchants,
    }

    return response


def get_favorite_merchants(customer):

    if is_frequent(customer=customer):
        orders = Order.objects.filter(
            customer=customer,
            odoo_order_state="done"
        )

        favorite_mw_offer_ids = orders.values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")

        if favorite_mw_offer_ids.count() > 1:

            fav_merchants = []
            for favorite_mw_offer_id in favorite_mw_offer_ids:
                fav_merchant = Merchant.objects.filter(mw_offer_id=favorite_mw_offer_id.get("mw_offer_id")).first()

                if orders.filter(rating__lte=3, mw_offer_id=fav_merchant.mw_offer_id).count() > 0:
                    pass

                else:
                    fav_merchants.append(
                        {
                            "mw_offer_id": int(fav_merchant.mw_offer_id),
                            "offer_name": fav_merchant.name,
                            "mw_neighborhood_id": int(fav_merchant.neighborhood.mw_id),
                            "neighborhood_name": fav_merchant.neighborhood.name,
                            "order_count": int(orders.filter(mw_offer_id=fav_merchant.mw_offer_id).count())
                        }
                    )

            response = {
                "favorite_merchants": fav_merchants
            }

        elif orders.filter(rating__gte=4).count() > 0:
            fav_merchant = Merchant.objects.filter(mw_offer_id=favorite_mw_offer_ids.get("mw_offer_id")).first()

            response = {
                "favorite_merchants": [
                    {
                        "mw_offer_id": int(fav_merchant.mw_offer_id),
                        "offer_name": fav_merchant.name,
                        "mw_neighborhood_id": int(fav_merchant.neighborhood.mw_id),
                        "neighborhood_name": fav_merchant.neighborhood.name,
                        "order_count": int(orders.filter(mw_offer_id=fav_merchant.mw_offer_id).count()),
                    }
                ]
            }

        else:
            response = {
                "favorite_merchants": []
            }

    else:
        response = {
            "favorite_merchants": []
        }

    return response


def get_most_viewed_offer(customer):

    if has_viewed_offer(customer=customer):
        favorite_viewed_offers = IntercomEvent.objects.filter(
            customer=customer,
            event_name="viewed offer",
        ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")[:4]

        most_viewed_offers = []
        for favorite_viewed_offer in favorite_viewed_offers:
            most_viewed_merchant = Merchant.objects.filter(mw_offer_id=favorite_viewed_offer.get("mw_offer_id")).first()

            most_viewed_offers.append(
                {
                    "mw_offer_id": int(most_viewed_merchant.mw_offer_id),
                    "offer_name": most_viewed_merchant.name,
                    "mw_neighborhood_id": int(most_viewed_merchant.neighborhood.mw_id),
                    "neighborhood_name": most_viewed_merchant.neighborhood.name,
                    "counter": favorite_viewed_offer.get("nb"),
                }
            )

        response = {
            "most_viewed_offers": most_viewed_offers,
        }

    else:
        response = {
            "most_viewed_offers": [],
        }

    return response


# from please_marketing_recommendation.recommendation_system import *
def get_cos_sim_recommendation(customer):

    if is_active(customer=customer) and CosineSimilarityBooking.objects.filter(
                Q(customer_1=customer) | Q(customer_2=customer),
                cos_sim_value__gte=0.7).count() > 0:

        cos_sims = CosineSimilarityBooking.objects.filter(
            Q(customer_1=customer) | Q(customer_2=customer),
            cos_sim_value__gte=0.7,
        )

        # GETTING SIMILAR USER
        similar_user_list = []
        for cos_sim in cos_sims:
            if cos_sim.customer_1 == customer:
                similar_user_list.append(cos_sim.customer_2)
            else:
                similar_user_list.append(cos_sim.customer_1)

        # GETTING SIMILAR VECTOR BOOKINGS
        vector_booking_customer = VectorBooking.objects.get(
            customer=customer,
        )

        vector_len = len(vector_booking_customer.vector)

        vector_bookings_similar_users = VectorBooking.objects.filter(
            customer__in=similar_user_list,
            vector__len=vector_len,
        )

        # MATRIX OF SIMILAR USER VECTOR BOOKING AND SUM OF EVERY COLUMNS
        vector_list_similar_users = []
        for vector in vector_bookings_similar_users:
            vector_list_similar_users.append(vector.vector)

        matrix = np.array(vector_list_similar_users)

        print(matrix.shape, matrix)

        final_vector = np.sum(matrix, axis=0)

        print(final_vector)

        # RETRIEVING MERCHANT FROM FINAL VECTOR EXCLUDING ALREADY BOOKED MERCHANT
        rank = 0
        mw_offer_id_weighted_list = []
        while rank < matrix.shape[1]:
            if (vector_booking_customer.vector[rank] == 0) and (final_vector[rank] > 2):
                mw_offer_id_weighted_list.append(
                    (vector_booking_customer.vector_merchant.vector[rank], final_vector[rank]))

            rank = rank + 1

        print(mw_offer_id_weighted_list)

        cos_sim_recommendations = []
        for mw_offer_id_weighted in sorted(mw_offer_id_weighted_list, key=itemgetter(1), reverse=True):
            try:
                merchant = Merchant.objects.get(mw_offer_id=mw_offer_id_weighted[0])

                cos_sim_recommendations.append(
                    {
                        "mw_offer_id": int(merchant.mw_offer_id),
                        "offer_name": merchant.name,
                        "mw_neighborhood_id": int(merchant.neighborhood.mw_id),
                        "neighborhood_name": merchant.neighborhood.name,
                        "recommendation_weight": int(mw_offer_id_weighted[1]),
                    }
                )

            except AttributeError:
                pass

        print(cos_sim_recommendations)

        response = {
            "cos_sim_recommendations": cos_sim_recommendations
        }

    else:
        response = {
            "cos_sim_recommendations": []
        }

    return response


# from please_marketing_recommendation.recommendation_system import *
def get_best_buying_moment(customer):

    if is_activated(customer=customer):

        orders = Order.objects.filter(
            customer=customer,
            odoo_order_state="done",
        ).order_by("-order_date")

        orders_date_time = orders.values("order_date")

        # DETERMINING THE BEST DAY TO SEND CAMPAIGN
        best_days = []
        for order_date_time in orders_date_time:
            best_days.append(
                order_date_time.get("order_date").date().strftime('%A')
            )
        best_day = sorted(best_days, key=best_days.count, reverse=True)[0]

        # DETERMINING THE BEST MOMENT (WEEK OR WEEKEND) TO SEND CAMPAIGN
        best_moments = []
        for order_date_time in orders_date_time:
            best_moments.append(
                get_best_day(day=order_date_time.get("order_date").date().strftime('%A'))
            )
        best_week_moment = sorted(best_moments, key=best_moments.count, reverse=True)[0]

        # DETERMINING THE BEST HOUR (MORNING OR NOON OR NIGHT) TO SEND CAMPAIGN
        best_hours = []
        for order_date_time in orders_date_time:
            best_hours.append(
                get_best_hour(hour=get_proper_datetime_tz(
                    date_time=order_date_time.get("order_date"),
                    neighborhood=customer.neighborhood,
                ).hour)
            )
        best_hours = sorted(best_hours, key=best_hours.count, reverse=True)[0]

        response = {
            "best_buying_moment_day": best_day.upper(),  # DAY
            "best_buying_moment_of_the_week": best_week_moment,  # WEEKDAYS vs WEEKEND
            "best_buying_moment_hour": best_hours,  # MORNING vs NOON vs NIGHT
        }

    elif has_viewed_offer(customer=customer):

        intercom_events = IntercomEvent.objects.filter(
            Q(event_name="viewed offer") | Q(event_name="viewed universe") | Q(event_name="viewed home page"),
            customer=customer,
            created_at__isnull=False,
        )

        print(intercom_events)

        events_date_time = intercom_events.values("created_at")

        # DETERMINING THE BEST DAY TO SEND CAMPAIGN
        best_days = []
        for event_date_time in events_date_time:
            best_days.append(
                event_date_time.get("created_at").date().strftime('%A')
            )
        best_day = sorted(best_days, key=best_days.count, reverse=True)[0]

        # DETERMINING THE BEST MOMENT (WEEK OR WEEKEND) TO SEND CAMPAIGN
        best_moments = []
        for event_date_time in events_date_time:
            best_moments.append(
                get_best_day(day=event_date_time.get("created_at").date().strftime('%A'))
            )
        best_week_moment = sorted(best_moments, key=best_moments.count, reverse=True)[0]

        # DETERMINING THE BEST HOUR (MORNING OR NOON OR NIGHT) TO SEND CAMPAIGN
        best_hours = []
        for event_date_time in events_date_time:
            best_hours.append(
                get_best_hour(hour=get_proper_datetime_tz(
                    date_time=event_date_time.get("order_date"),
                    neighborhood=customer.neighborhood,
                ).hour)
            )
        best_hours = sorted(best_hours, key=best_hours.count, reverse=True)[0]

        response = {
            "best_buying_moment_day": best_day.upper(),  # DAY
            "best_buying_moment_of_the_week": best_week_moment,  # WEEKDAYS vs WEEKEND
            "best_buying_moment_hour": best_hours,  # MORNING vs NOON vs NIGHT
        }

    else:

        response = {
            "best_buying_moment_day": "",  # DAY
            "best_buying_moment_of_the_week": "",  # WEEKDAYS vs WEEKEND
            "best_buying_moment_hour": "",  # MORNING vs NOON vs NIGHT
        }

    return response


# from please_marketing_recommendation.recommendation_system import *
def get_recommendation(customer):

    response = {
        "customer_email": customer.email,
        "is_active": is_active(customer=customer),
        "is_activated": is_activated(customer=customer),
        "is_frequent": is_frequent(customer=customer),
        "favorite_universe": "" if not get_trending_merchants(customer=customer).get("trending_merchants") else get_trending_merchants(customer=customer).get("trending_merchants")[0].get("universe_name"),
    }

    response.update(get_device(customer=customer))
    response.update(get_trending_merchants(customer=customer))
    response.update(get_cos_sim_recommendation(customer=customer))
    response.update(get_favorite_merchants(customer=customer))
    response.update(get_most_viewed_offer(customer=customer))
    response.update(get_orders(customer=customer))
    response.update(get_best_buying_moment(customer=customer))

    return response
