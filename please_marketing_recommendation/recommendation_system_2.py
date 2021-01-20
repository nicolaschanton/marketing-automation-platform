# coding: utf-8

from please_marketing_app.models import Customer, Fete, Merchant, IntercomEvent, NotificationHistory, Order, \
    NetPromoterScore, SmsHistory, Neighborhood, OrderLine, SalesAnalysis
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
from random import randint
import math
from django.db.models import Sum, Avg


# from please_marketing_recommendation.recommendation_system import *
# customer = Customer.objects.filter().order_by("?").first()
# print(customer, customer.neighborhood)
def is_activated(customer):
    customer_orders = 0 if not customer.orders_number else customer.orders_number

    response = True if customer_orders > 0 else False

    return response


def is_active(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        created_at__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=60)).strftime("%s"))),
    ).count()

    customer_orders = 0 if not customer.orders_number else customer.orders_number

    response = True if ((customer_orders > 0) and (ie_count > 0)) else False

    return response


def is_frequent(customer):
    ie_count = IntercomEvent.objects.filter(
        customer=customer,
        created_at__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=30)).strftime("%s"))),
    ).count()

    customer_orders = 0 if not customer.orders_number else customer.orders_number

    response = True if ((customer_orders > 4) and (ie_count > 0)) else False

    return response


def is_churning(customer):
    if is_activated(customer=customer):
        response = True if customer.last_order_date < (datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=60)) else False

    else:
        response = False

    return response


def is_hard_to_activate(customer):
    if not is_activated(customer=customer):
        response = True if customer.sign_up_date < (datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=60)) else False

    else:
        response = False

    return response


def is_bankable(customer):

    if customer.total_voucher > 0:
        total_spent = customer.total_spent
        total_voucher = customer.total_voucher

        ratio = total_voucher / total_spent

        response = True if ratio < 0.07 else False

    else:
        response = True

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
        universe_name__isnull=False,
    ).exclude(universe_name="").values("universe_name").distinct("universe_name")

    similarity_tuple = []
    for clean_universe_queryset_raw in clean_universe_queryset:
        clean_universe_name = clean_universe_queryset_raw.get("universe_name")

        similarity_tuple.append(
            (
                clean_universe_name,
                raw_universe_name,
                SequenceMatcher(None, raw_universe_name.lower(), clean_universe_name.lower()).ratio()
            )
        )

    result = sorted(similarity_tuple, key=itemgetter(2), reverse=True)[0][0]

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
            "main_device": device
        }
        return response

    else:
        response = {
            "main_device": ""
        }
        return response


def get_most_converting_merchant(customer):

    if is_active(customer=customer):

        orders = Order.objects.filter(
            customer=customer,
            neighborhood=customer.neighborhood,
            odoo_order_state="done",
        )

        viewed_offers = IntercomEvent.objects.filter(
            customer=customer,
            neighborhood=customer.neighborhood,
            event_name="viewed offer",
            mw_offer_id__isnull=False
        )

        raw_merchant_ids = orders.values("mw_offer_id").distinct("mw_offer_id")
        merchant_ids = []
        for raw_merchant_id in raw_merchant_ids:
            merchant_ids.append(
                raw_merchant_id.get("mw_offer_id")
            )

        result_list = []
        for merchant in Merchant.objects.filter(mw_offer_id__in=merchant_ids):
                order_count = orders.filter(mw_offer_id=merchant.mw_offer_id).count()
                vo_count = viewed_offers.filter(mw_offer_id=merchant.mw_offer_id).count()
                ratio = 0 if (order_count == 0 or vo_count == 0) else order_count / vo_count

                result_list.append(
                    (merchant, ratio)
                )

        merchant = sorted(result_list, key=itemgetter(1), reverse=True)[0][0]
        conversion_ratio = sorted(result_list, key=itemgetter(1), reverse=True)[0][1]

        response = {
            "most_converting_merchant": {
                "mw_offer_id": int(merchant.mw_offer_id),
                "offer_name": merchant.name,
                "mw_neighborhood_id": int(merchant.neighborhood.mw_id),
                "neighborhood_name": merchant.neighborhood.name,
                "ratio": conversion_ratio,
            }
        }

    else:
        response = {
            "most_converting_merchant": {
                "mw_offer_id": "",
                "offer_name": "",
                "mw_neighborhood_id": "",
                "neighborhood_name": "",
                "ratio": "",
            }
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
            order_date__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=90)).strftime("%s"))),
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
            order_date__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=90)).strftime("%s"))),
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
            order_date__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=90)).strftime("%s"))),
        ).values("mw_offer_id").annotate(nb=Count("mw_offer_id")).order_by("-nb")[:4]

    else:
        trending_merchant_ids = Order.objects.filter(
            neighborhood=customer.neighborhood,
            odoo_order_state="done",
            order_date__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=90)).strftime("%s"))),
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
                            float((datetime(2020, 1, 1) - timedelta(days=90)).strftime("%s"))
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

                if orders.filter(rating__gt=3, mw_offer_id=fav_merchant.mw_offer_id).count() > 0:
                    fav_merchants.append(
                        {
                            "mw_offer_id": int(fav_merchant.mw_offer_id),
                            "offer_name": fav_merchant.name,
                            "mw_neighborhood_id": int(fav_merchant.neighborhood.mw_id),
                            "neighborhood_name": fav_merchant.neighborhood.name,
                            "order_count": int(orders.filter(mw_offer_id=fav_merchant.mw_offer_id).count())
                        }
                    )

                else:
                    pass

            response = {
                "favorite_merchants": fav_merchants
            }

        elif orders.filter(Q(rating__gte=4) | Q(rating=0)).count() > 0:
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
            if Merchant.objects.filter(mw_offer_id=favorite_viewed_offer.get("mw_offer_id")).count() == 1:
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

        final_vector = np.sum(matrix, axis=0)

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


def has_cos_sim_orders_recommendation(customer):
    response = False if not get_cos_sim_recommendation(customer=customer).get("cos_sim_recommendations") else True

    return response


# from please_marketing_recommendation.recommendation_system import *
def get_best_buying_moment(customer):

    if is_activated(customer=customer):

        orders = Order.objects.filter(
            customer=customer,
            odoo_order_state="done",
            order_date__isnull=False,
            order_date__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=720)).strftime("%s"))),
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
            created_at__gt=datetime.fromtimestamp(float((datetime(2020, 1, 1) - timedelta(days=720)).strftime("%s"))),
        )

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
                    date_time=event_date_time.get("created_at"),
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


def get_best_voucher_value(customer):

    if is_active(customer=customer):
        response = {
            "voucher_recommendations": {
                "deserve_voucher": False,
                "voucher_type": "amount",
                "voucher_value": 0,
            }
        }

    elif is_activated(customer=customer):
        if is_churning(customer=customer):
            if is_bankable(customer=customer):
                response = {
                    "voucher_recommendations": {
                        "deserve_voucher": True,
                        "voucher_type": "amount",
                        "voucher_value": 5,
                    }
                }
            else:
                response = {
                    "voucher_recommendations": {
                        "deserve_voucher": True,
                        "voucher_type": "percent",
                        "voucher_value": 10,
                    }
                }
        else:
            response = {
                "voucher_recommendations": {
                    "deserve_voucher": False,
                    "voucher_type": "amount",
                    "voucher_value": 0,
                }
            }
    else:
        if is_hard_to_activate(customer=customer):

            response = {
                "voucher_recommendations": {
                    "deserve_voucher": False,
                    "voucher_type": "amount",
                    "voucher_value": 10,
                }
            }

        else:
            response = {
                "voucher_recommendations": {
                    "deserve_voucher": False,
                    "voucher_type": "amount",
                    "voucher_value": 5,
                }
            }

    return response


def get_household_composition(customer):

    if is_active(customer=customer):

        orders = Order.objects.filter(
            customer=customer,
            odoo_order_state="done",
            basket_amount__gt=15,
            basket_amount__lt=80,
        )

        list_of_item_number_by_order = []
        list_of_item_price_by_order = []
        for order in orders:
            order_lines = OrderLine.objects.filter(
                odoo_order_id=order.odoo_order_id,
                total_amount__gte=0,
            ).exclude(label__icontains="Retrait sur place")\
                .exclude(label__icontains="Please - Frais bancaires et de gestion")\
                .exclude(label__icontains="Participation aux frais de livraison")

            basket_amount = order_lines.aggregate(Sum('total_amount')).get("total_amount__sum")
            item_quantity = order_lines.aggregate(Sum('quantity')).get("quantity__sum")

            if "restaurant" in order.universe_name.lower():
                nb_people = basket_amount / 13

            elif "fast" in order.universe_name.lower():
                nb_people = basket_amount / 9

            elif "déjeuner" in order.universe_name.lower():
                nb_people = basket_amount / 7

            else:
                nb_people = basket_amount / 10

            list_of_item_number_by_order.append(
                (basket_amount, item_quantity, nb_people)
            )

            l1 = []
            for item in order_lines:
                x = int(item.quantity)
                while x > 0:
                    l1.append(
                        (item.total_amount / item.quantity, item.label)
                    )
                    x = x - 1

            list_of_item_price_by_order.append(l1)

        average_people = sum(k for i, j, k in list_of_item_number_by_order) / len(list_of_item_number_by_order)
        response = {
            "nb_people_average": average_people,
            "nb_people_average_2": list_of_item_price_by_order,
        }

    else:
        response = {
            "nb_people_average": "",
        }

    return response


#def get_best_choice(customer, cos_sim_recommendations):
#
#    if is_activated(customer=customer):
#
#        if has_cos_sim_orders_recommendation(customer=customer):
#
#            if len(cos_sim_recommendations.get("cos_sim_recommendations")) > 2:
#
#                max_list_length = len(cos_sim_recommendations.get("cos_sim_recommendations")) - 1
#
#                random_choice_coin = randint(0, 1)
#
#                if random_choice_coin == 0:
#                    best_choice = {
#                        "best_choice": cos_sim_recommendations.get("cos_sim_recommendations")[0],
#                    }
#
#                else:
#                    max_first_half = math.ceil(max_list_length / 2)
#                    random_choice = randint(1, int(max_first_half))
#                    best_choice = {
#                        "best_choice": cos_sim_recommendations.get("cos_sim_recommendations")[random_choice],
#                    }
#
#            else:
#                random_choice = randint(0, 1)
#                best_choice = {
#                    "best_choice": cos_sim_recommendations.get("cos_sim_recommendations")[random_choice],
#                }
#
#        elif is_frequent(customer=customer):
#            # Obsessed Customer with one particular merchant
#
#
#            #
#
#            #
#
#        else:
#
#
#    else:
#
#
#    return best_choice


# from please_marketing_recommendation.recommendation_system import *
def get_recommendation(customer):

    # cos_sim_recommendations = get_cos_sim_recommendation(customer=customer)

    response = {
        "customer_odoo_id": customer.odoo_user_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "customer_satisfaction": customer.average_rating,
        "gender": customer.gender,
        "is_active": is_active(customer=customer),
        "is_activated": is_activated(customer=customer),
        "is_frequent": is_frequent(customer=customer),
        "is_churning": is_churning(customer=customer),
        "favorite_universe": "" if not get_trending_merchants(customer=customer).get("trending_merchants") else get_trending_merchants(customer=customer).get("trending_merchants")[0].get("universe_name"),
    }

    response.update(get_household_composition(customer=customer))
    response.update(get_device(customer=customer))
    response.update(get_best_buying_moment(customer=customer))
    response.update(get_best_voucher_value(customer=customer))
    response.update(get_trending_merchants(customer=customer))
    response.update(get_favorite_merchants(customer=customer))
    response.update(get_most_converting_merchant(customer=customer))
    response.update(get_most_viewed_offer(customer=customer))
    response.update(get_orders(customer=customer))
    # response.update(cos_sim_recommendations)
    # response.update(best_choice(customer=customer, cos_sim_recommendations=cos_sim_recommendations))

    return response


# from please_marketing_recommendation.recommendation_system import *
