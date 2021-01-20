# coding: utf-8

from please_marketing_app.models import Customer, Order, NetPromoterScore, SalesAnalysis, \
    Merchant, IntercomEvent, OrderLine, Neighborhood
from please_marketing_extra_user_enrichment.models import AddressEnrichmentSl
from please_marketing_landing_pages.models import Lead
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Avg, Count, Min, Sum
import sys
from concurrent.futures import ThreadPoolExecutor
from please_marketing_script_execution.log_script import log_script
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import csv
from io import StringIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from django.db.models import Q, Value
from django.db import models


# https://info.recurly.com/research/churn-rate-benchmarks => CHECK AVERAGE CHURN RATES
# from please_marketing_app.main_scripts.kpis import *
def bm_evreux():

    order_number_done_60 = Order.objects.filter(
        odoo_order_state="done",
        neighborhood=Neighborhood.objects.get(mw_id=5),
        order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s"))),
    ).values("offer_name").annotate(total=Count('offer_name')).order_by('-total')

    print(order_number_done_60)

    return


def analyze_bk():
    csvfile = StringIO()

    fieldnames = [
        "quantity",
        "label",
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for order in Order.objects.filter(mw_offer_id=12456, odoo_order_state='done'):
        for order_line in OrderLine.objects.filter(odoo_order_id=order.odoo_order_id)\
                .exclude(label__contains="bancaires et de gestion")\
                .exclude(label__contains="frais de livraison"):
            writer.writerow(
                {
                    "quantity": order_line.quantity,
                    "label": order_line.label,
                }
            )

            print(order_line.quantity, order_line.label)

    email = EmailMessage(
        '[CONFIDENTIAL] Export BK Orders',
        '',
        'Please <contact@pleaseapp.com>',
        ['nicolas.chanton@pleaseapp.com'],
    )
    email.attach('export_bk.csv', csvfile.getvalue(), 'text/csv')
    email.send()

    return


def calculate_ltv_global():
    orders_current_year = Order.objects.filter(
        odoo_order_state='done',
        order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=365)).strftime("%s"))),
    )

    customers_previous_year = Order.objects.filter(
        odoo_order_state='done',
        order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=730)).strftime("%s"))),
        order_date__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=365)).strftime("%s"))),
    ).values_list('customer', flat=True).distinct()

    customers_previous_year_still_active_current_year = Order.objects.filter(
        customer__in=customers_previous_year,
        odoo_order_state='done',
        order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=365)).strftime("%s"))),
    ).values_list('customer', flat=True).distinct()

    average_basket = orders_current_year.aggregate(Avg('basket_amount')).get('basket_amount__avg')
    average_purchase_frequency_rate = orders_current_year.count() / orders_current_year.values_list('customer',
                                                                                                    flat=True).distinct().count()
    customer_value = average_basket * average_purchase_frequency_rate
    churn_rate = 1 - (customers_previous_year_still_active_current_year.count() / customers_previous_year.count())
    average_customer_lifespan = 1 / churn_rate
    lifetime_value = customer_value * average_customer_lifespan

    return average_basket, average_purchase_frequency_rate, customer_value, churn_rate, average_customer_lifespan, lifetime_value


def calculate_average_discount_per_order():
    orders = Order.objects.filter(odoo_order_state='done')

    adpo = orders.aggregate(Sum('voucher_amount')).get('voucher_amount__sum') / orders.count()

    return adpo


def calculate_average_basket():
    orders = Order.objects.filter(odoo_order_state='done')

    ab = orders.aggregate(Avg('basket_amount')).get('basket_amount__avg')

    return ab


def nps_calculator():
    promoter = NetPromoterScore.objects.filter(score__gte=9).count()
    passive = NetPromoterScore.objects.filter(score__gte=7, score__lte=8).count()
    detractor = NetPromoterScore.objects.filter(score__lte=6).count()

    total_responses = promoter + passive + detractor

    nps = ((promoter - detractor) / total_responses) * 100

    return nps


def csat_calculator():
    csat = NetPromoterScore.objects.all().aggregate(Avg('score')).get('score__avg')

    return csat


def calculate_orders_distribution():
    no_order = Customer.objects.filter(orders_number__lt=1).count()
    activated = Customer.objects.filter(orders_number__gt=0).count()
    one_order = Customer.objects.filter(orders_number=1).count()
    two_order = Customer.objects.filter(orders_number=2).count()
    three_order = Customer.objects.filter(orders_number=3).count()
    four_order = Customer.objects.filter(orders_number=4).count()
    five_order = Customer.objects.filter(orders_number=5).count()
    six_order = Customer.objects.filter(orders_number=6).count()
    more_order = Customer.objects.filter(orders_number__gt=6).count()

    return no_order, activated, one_order, two_order, three_order, four_order, five_order, six_order, more_order


def send_weekly_report():
    msg = EmailMessage(
        str("[CONFIDENTIAL] Marketing Weekly Report"),
        str(
            str(
                "# LTV (average_basket, average_purchase_frequency_rate, customer_value, churn_rate, average_customer_lifespan, lifetime_value)")
            + str("\n")
            + str("\n")
            + str(calculate_ltv_global())
            + str("\n")
            + str("\n")
            + str("# ADPO")
            + str("\n")
            + str("\n")
            + str(calculate_average_discount_per_order())
            + str("\n")
            + str("\n")
            + str("# AB")
            + str("\n")
            + str("\n")
            + str(calculate_average_basket())
            + str("\n")
            + str("\n")
            + str("# NPS")
            + str("\n")
            + str("\n")
            + str(nps_calculator())
            + str("\n")
            + str("\n")
            + str("# CSAT")
            + str("\n")
            + str("\n")
            + str(csat_calculator())
            + str("\n")
            + str("\n")
            + str(
                "# ORDERS DISTRIBUTION (no_order, activated, one_order, two_order, three_order, four_order, five_order, six_order, more_order)")
            + str("\n")
            + str("\n")
            + str(calculate_orders_distribution())
            + str("\n")
            + str("\n")
            + str("\n")
            + str("NE PAS DIFFUSER")
        ),
        "Please <contact@pleaseapp.com>",
        ["nicolas.chanton@pleaseapp.com"],
    )
    msg.send()

    return


# from please_marketing_app.main_scripts.kpis import *
def analyze_merchant(merchant):
    try:
        if Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
        ).count() > 5:

            order_number_done = Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
            )
            order_number_done_30 = Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
                order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s"))),
            )
            order_number_done_60 = Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
                order_date__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s"))),
                order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s"))),
            )

            order_number_done_rated = Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
                rating__gt=0
            )
            order_number_done_rated_30 = Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
                rating__gt=0,
                order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s"))),
            )
            order_number_done_rated_60 = Order.objects.filter(
                odoo_order_state="done",
                mw_offer_id=merchant.mw_offer_id,
                rating__gt=0,
                order_date__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s"))),
                order_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s"))),
            )

            viewed_offer_all = IntercomEvent.objects.filter(
                event_name="viewed offer",
                mw_offer_id=merchant.mw_offer_id,
            )
            viewed_offer_all_30 = IntercomEvent.objects.filter(
                event_name="viewed offer",
                mw_offer_id=merchant.mw_offer_id,
                created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s")))

            )
            viewed_offer_all_60 = IntercomEvent.objects.filter(
                event_name="viewed offer",
                mw_offer_id=merchant.mw_offer_id,
                created_at__lt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s"))),
                created_at__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=60)).strftime("%s")))

            )

            def get_trend(v_30, v_60):

                if (v_30 is not None) and (v_60 is not None):
                    if (v_30 > 0) and (v_60 > 0):

                        trend = (v_30 - v_60) / v_60

                    else:
                        trend = None
                else:
                    trend = None

                return trend

            # INDICATORS CALCULATION
            order_number = order_number_done.count()
            order_number_30 = order_number_done_30.count()
            order_number_60 = order_number_done_60.count()
            order_number_trend = get_trend(v_30=order_number_30, v_60=order_number_60)

            viewed_offer = viewed_offer_all.count()
            viewed_offer_30 = viewed_offer_all_30.count()
            viewed_offer_60 = viewed_offer_all_60.count()
            viewed_offer_trend = get_trend(v_30=viewed_offer_30, v_60=viewed_offer_60)

            po_vo_ratio = order_number / viewed_offer
            po_vo_ratio_30 = order_number_30 / viewed_offer_30
            po_vo_ratio_60 = order_number_60 / viewed_offer_60
            po_vo_ratio_trend = get_trend(v_30=po_vo_ratio_30, v_60=po_vo_ratio_60)

            average_rating = order_number_done_rated.aggregate(Avg("rating")).get("rating__avg")
            average_rating_30 = order_number_done_rated_30.aggregate(Avg("rating")).get("rating__avg")
            average_rating_60 = order_number_done_rated_60.aggregate(Avg("rating")).get("rating__avg")
            average_rating_trend = get_trend(v_30=average_rating_30, v_60=average_rating_60)

            average_basket = order_number_done.aggregate(Avg("basket_amount")).get("basket_amount__avg")
            average_basket_30 = order_number_done_30.aggregate(Avg("basket_amount")).get("basket_amount__avg")
            average_basket_60 = order_number_done_60.aggregate(Avg("basket_amount")).get("basket_amount__avg")
            average_basket_trend = get_trend(v_30=average_basket_30, v_60=average_basket_60)

            average_please_amount = order_number_done.aggregate(Avg("please_amount")).get("please_amount__avg")
            average_please_amount_30 = order_number_done_30.aggregate(Avg("please_amount")).get("please_amount__avg")
            average_please_amount_60 = order_number_done_60.aggregate(Avg("please_amount")).get("please_amount__avg")
            average_please_amount_trend = get_trend(v_30=average_please_amount_30, v_60=average_please_amount_60)

            average_partner_amount = order_number_done.aggregate(Avg("partner_amount")).get("partner_amount__avg")
            average_partner_amount_30 = order_number_done_30.aggregate(Avg("partner_amount")).get("partner_amount__avg")
            average_partner_amount_60 = order_number_done_60.aggregate(Avg("partner_amount")).get("partner_amount__avg")
            average_partner_amount_trend = get_trend(v_30=average_partner_amount_30, v_60=average_partner_amount_60)

            if SalesAnalysis.objects.filter(merchant=merchant).count() == 0:
                SalesAnalysis(
                    merchant=merchant,
                    viewed_offer=viewed_offer,
                    viewed_offer_30=viewed_offer_30,
                    viewed_offer_60=viewed_offer_60,
                    viewed_offer_trend=viewed_offer_trend,

                    po_vo_ratio=po_vo_ratio,
                    po_vo_ratio_30=po_vo_ratio_30,
                    po_vo_ratio_60=po_vo_ratio_60,
                    po_vo_ratio_trend=po_vo_ratio_trend,

                    average_rating=average_rating,
                    average_rating_30=average_rating_30,
                    average_rating_60=average_rating_60,
                    average_rating_trend=average_rating_trend,

                    average_basket=average_basket,
                    average_basket_30=average_basket_30,
                    average_basket_60=average_basket_60,
                    average_basket_trend=average_basket_trend,

                    average_please_amount=average_please_amount,
                    average_please_amount_30=average_please_amount_30,
                    average_please_amount_60=average_please_amount_60,
                    average_please_amount_trend=average_please_amount_trend,

                    average_partner_amount=average_partner_amount,
                    average_partner_amount_30=average_partner_amount_30,
                    average_partner_amount_60=average_partner_amount_60,
                    average_partner_amount_trend=average_partner_amount_trend,

                    order_number=order_number,
                    order_number_30=order_number_30,
                    order_number_60=order_number_60,
                    order_number_trend=order_number_trend,
                ).save()

            elif SalesAnalysis.objects.filter(merchant=merchant).count() == 1:
                sales_analysis = SalesAnalysis.objects.get(merchant=merchant)
                sales_analysis.merchant = merchant

                sales_analysis.viewed_offer = viewed_offer
                sales_analysis.viewed_offer_30 = viewed_offer_30
                sales_analysis.viewed_offer_60 = viewed_offer_60
                sales_analysis.viewed_offer_trend = viewed_offer_trend

                sales_analysis.po_vo_ratio = po_vo_ratio
                sales_analysis.po_vo_ratio_30 = po_vo_ratio_30
                sales_analysis.po_vo_ratio_60 = po_vo_ratio_60
                sales_analysis.po_vo_ratio_trend = po_vo_ratio_trend

                sales_analysis.average_rating = average_rating
                sales_analysis.average_rating_30 = average_rating_30
                sales_analysis.average_rating_60 = average_rating_60
                sales_analysis.average_rating_trend = average_rating_trend

                sales_analysis.average_basket = average_basket
                sales_analysis.average_basket_30 = average_basket_30
                sales_analysis.average_basket_60 = average_basket_60
                sales_analysis.average_basket_trend = average_basket_trend

                sales_analysis.average_please_amount = average_please_amount
                sales_analysis.average_please_amount_30 = average_please_amount_30
                sales_analysis.average_please_amount_60 = average_please_amount_60
                sales_analysis.average_please_amount_trend = average_please_amount_trend

                sales_analysis.average_partner_amount = average_partner_amount
                sales_analysis.average_partner_amount_30 = average_partner_amount_30
                sales_analysis.average_partner_amount_60 = average_partner_amount_60
                sales_analysis.average_partner_amount_trend = average_partner_amount_trend

                sales_analysis.order_number = order_number
                sales_analysis.order_number_30 = order_number_30
                sales_analysis.order_number_60 = order_number_60
                sales_analysis.order_number_trend = order_number_trend

                sales_analysis.save()

            else:
                pass

    except:
        print("ERROR: " + str(sys.exc_info()))

    return


# from please_marketing_app.main_scripts.kpis import *
def executor_analyze_merchant():
    log_script(name="executor_analyze_merchant", status="s")

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(
            analyze_merchant,
            Merchant.objects.filter(
                active=True,
                mw_offer_id__isnull=False).order_by("neighborhood")
        )

    log_script(name="executor_analyze_merchant", status="d")
    return


# from please_marketing_app.main_scripts.kpis import *
def send_landing_pages_report():
    csvfile = StringIO()

    fieldnames = [
        "email",
        "first_name",
        "last_name",
        "phone",
        "raw_address",
        "street",
        "city",
        "zip",
        "neighborhood",
        "img_name",
        "txt_name",
        "search_term",
        "signed_up_please",
        "odoo_user_id",
        "created_date",
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for lead in Lead.objects.filter(email__isnull=False, signed_up_please=True):
        writer.writerow(
            {
                "email": lead.email,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "phone": lead.phone,
                "raw_address": lead.raw_address,
                "street": lead.street,
                "city": lead.city,
                "zip": lead.zip,
                "neighborhood": None if not lead.neighborhood else lead.neighborhood.name,
                "img_name": lead.img_name,
                "txt_name": lead.txt_name,
                "search_term": lead.search_term,
                "signed_up_please": lead.signed_up_please,
                "odoo_user_id": lead.odoo_user_id,
                "created_date": lead.created_date.strftime("%Y/%m/%d"),
            }
        )

    for lead_value in Lead.objects.filter(email__isnull=False, signed_up_please=False).values('email').distinct():

        lead = Lead.objects.filter(email=lead_value.get("email"), signed_up_please=False).first()

        if lead:
            writer.writerow(
                {
                    "email": lead.email,
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "phone": lead.phone,
                    "raw_address": lead.raw_address,
                    "street": lead.street,
                    "city": lead.city,
                    "zip": lead.zip,
                    "neighborhood": None if not lead.neighborhood else lead.neighborhood.name,
                    "img_name": lead.img_name,
                    "txt_name": lead.txt_name,
                    "search_term": lead.search_term,
                    "signed_up_please": lead.signed_up_please,
                    "odoo_user_id": lead.odoo_user_id,
                    "created_date": lead.created_date.strftime("%Y/%m/%d"),
                }
            )

    email = EmailMessage(
        '[CONFIDENTIAL] Export des Leads Landing Pages',
        '',
        'Please <contact@pleaseapp.com>',
        ['nicolas.chanton@pleaseapp.com', 'francois.rabier@pleaseapp.com'],
    )
    email.attach('export_landing_pages.csv', csvfile.getvalue(), 'text/csv')
    email.send()

    return


# def analyze_spending_distribution():
#     order_data = pd.DataFrame.from_records(
#         Order.objects.filter(
#             odoo_order_state="done",
#             customer__isnull=False,
#             basket_amount__gt=0,
#         ).values(
#             "customer",
#             "basket_amount",
#         )
#     )
#
#     nn = order_data.groupby(by=["customer"])
#     nn_sum = nn.sum().sort_values(by=['basket_amount'], ascending=False)
#     nn_sum_cleared = nn_sum[nn_sum.basket_amount < 4400]
#
#     print(nn_sum_cleared)
#
#     nn_sum_cleared.plot(
#         kind='bar',
#         title='Spending Distribution per User in Please',
#         color='#FFCD00',
#         use_index=False,
#     ).set(
#         xlabel='Users',
#         ylabel='Spendings (€)',
#     )
#
#     plt.tick_params(
#         axis='x',
#         which='both',
#         bottom=False,
#         top=False,
#         labelbottom=False)
#
#     legend = plt.legend()
#     legend.get_texts()[0].set_text('Total Spent')
#
#     # sns.boxplot(x=nn_sum_cleared['basket_amount'])
#
#     plt.show()
#
#     return
#
#
# # from please_marketing_app.main_scripts.kpis import *
# def analyze_housing_vs_total_spent():
#     order_data = pd.DataFrame.from_records(
#         Order.objects.filter(
#             odoo_order_state='done',
#             basket_amount__gt=0,
#             customer__isnull=False,
#             customer__average_basket__gt=0,
#             customer__average_basket__lt=100,
#             customer__total_spent__gt=0,
#             customer__total_spent__lt=4400,
#         ).values(
#             "customer",
#             "universe_name",
#             "customer__neighborhood__name",
#             "customer__total_spent",
#             "customer__average_basket",
#             "customer__total_voucher",
#             "customer__gender",
#             "basket_amount",
#             "voucher_amount",
#         )
#     )
#
#     print(order_data)
#
#     sns.lmplot(
#         "voucher_amount",
#         "basket_amount",
#         data=order_data,
#         fit_reg=False,
#         hue="customer__gender",
#         # col='customer__neighborhood__name',
#         # col_wrap=2
#     )
#
#     # sns.pairplot(order_data.loc[:, order_data.dtypes == 'float64'])
#
#     plt.show()
#
#     return
#
#
# # from please_marketing_app.main_scripts.kpis import *
# def analyze_housing():
#     housing_data = pd.DataFrame.from_records(
#         AddressEnrichmentSl.objects.filter(
#             averageIncome__isnull=False,
#             customer__isnull=False,
#             customer__average_basket__gt=0,
#             # customer__average_basket__lt=100,
#             customer__total_spent__gt=0,
#             # customer__total_spent__lt=4400,
#             # peopleDensity__lt=10600,
#         ).values(
#             # "customer__total_spent",
#             # "customer__average_basket",
#             # "customer__total_voucher",
#             # "customer__gender",
#             # "customer__neighborhood__name",
#             "averageIncome",
#             "pcentActifsAll",
#             "pcentUnemployed",
#             "ageMed",
#             "peopleDensity",
#             "summary_prices_med",
#             # "single",
#             # "couple",
#             # "family",
#         )
#     )
#
#     print(housing_data)
#
#     sns.pairplot(
#         data=housing_data,
#         diag_kind="kde",
#         kind="reg",
#     )
#     plt.show()
#
#     # sns.lmplot(
#     #     "peopleDensity",
#     #     "peopleDensity",
#     #     data=housing_data,
#     #     fit_reg=False,
#     #     hue="customer__neighborhood__name",
#     #     # col='customer__neighborhood__name',
#     #     # col_wrap=2
#     # )
#     # plt.show()
#
#     # sns.pairplot(order_data.loc[:, order_data.dtypes == 'float64'])
#     # plt.show()
#
#     # corr = order_data.loc[:, order_data.dtypes == 'float64'].corr()
#     # sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns,
#     #             cmap=sns.diverging_palette(220, 10, as_cmap=True))
#     # plt.show()
#
#     return
#
#
# from please_marketing_app.main_scripts.kpis import *
def analyze_order_data():
    order_data = pd.DataFrame.from_records(
        Order.objects.filter(
            Q(universe_name="Fast Food") | Q(universe_name="Fast Food "),
            odoo_order_state="done",
            basket_amount__gt=0,
            basket_amount__lt=50,
        ).values(
            "basket_amount",
        )
    )

    g = sns.distplot(order_data)
    plt.show()

    return


# from please_marketing_app.main_scripts.kpis import *
def analyze_ie_data():
    event_data = pd.DataFrame.from_records(
        IntercomEvent.objects.filter(event_name="viewed offer").values(
            "device_model",
            "universe_name"
        )
    )

    sns.catplot(x="universe_name", kind="count", palette="ch:.25", data=event_data)
    plt.show()

    return


# from please_marketing_app.main_scripts.kpis import *
def iesex_data():

    restaurants = IntercomEvent.objects.filter(
            universe_name__icontains="restaurant",
            event_name="viewed offer",
        ).annotate(universe_name_2=Value("Restaurants", models.CharField())).values(
            "customer__gender",
            "universe_name_2"
        )

    fast_foods = IntercomEvent.objects.filter(
            universe_name__icontains="fast food",
            event_name="viewed offer",
        ).annotate(universe_name_2=Value("Fast Food", models.CharField())).values(
            "customer__gender",
            "universe_name_2"
        )

    breakfast = IntercomEvent.objects.filter(
        universe_name__icontains="petit",
        event_name="viewed offer",
    ).annotate(universe_name_2=Value("Petits-Déjeuners", models.CharField())).values(
        "customer__gender",
        "universe_name_2"
    )

    market = IntercomEvent.objects.filter(
        universe_name__icontains="course",
        event_name="viewed offer",
    ).annotate(universe_name_2=Value("Courses et Marché", models.CharField())).values(
        "customer__gender",
        "universe_name_2"
    )

    event_data_restaurants = pd.DataFrame.from_records(
        restaurants
    )

    event_data_fast_foods = pd.DataFrame.from_records(
        fast_foods
    )

    event_data_breakfast = pd.DataFrame.from_records(
        breakfast
    )

    event_data_market = pd.DataFrame.from_records(
        market
    )

    event_data = event_data_restaurants.append(
        event_data_fast_foods
    ).append(
        event_data_breakfast
    ).append(
        event_data_market
    )

    sns.catplot(
        y="universe_name_2",
        hue="customer__gender",
        kind="count",
        palette="pastel",
        edgecolor=".6",
        data=event_data
    )

    plt.show()

    return


def orsex_data():

    restaurants = Order.objects.filter(
            universe_name__icontains="restaurant",
            odoo_order_state="done"
        ).annotate(universe_name_2=Value("Restaurants", models.CharField())).values(
            "customer__gender",
            "universe_name_2"
        )

    fast_foods = Order.objects.filter(
            universe_name__icontains="fast food",
            odoo_order_state="done"
        ).annotate(universe_name_2=Value("Fast Food", models.CharField())).values(
            "customer__gender",
            "universe_name_2"
        )

    breakfast = Order.objects.filter(
            universe_name__icontains="petit",
            odoo_order_state="done"
    ).annotate(universe_name_2=Value("Petits-Déjeuners", models.CharField())).values(
        "customer__gender",
        "universe_name_2"
    )

    market = Order.objects.filter(
            universe_name__icontains="course",
            odoo_order_state="done"
    ).annotate(universe_name_2=Value("Courses et Marché", models.CharField())).values(
        "customer__gender",
        "universe_name_2"
    )

    order_data_restaurants = pd.DataFrame.from_records(
        restaurants
    )

    order_data_fast_foods = pd.DataFrame.from_records(
        fast_foods
    )

    order_data_breakfast = pd.DataFrame.from_records(
        breakfast
    )

    order_data_market = pd.DataFrame.from_records(
        market
    )

    order_data = order_data_restaurants.append(
        order_data_fast_foods
    ).append(
        order_data_breakfast
    ).append(
        order_data_market
    )

    sns.catplot(
        y="universe_name_2",
        hue="customer__gender",
        kind="count",
        palette="pastel",
        edgecolor=".6",
        data=order_data
    )

    plt.show()

    return


def oros_data():

    restaurants = Order.objects.filter(
            universe_name__icontains="restaurant",
            odoo_order_state="done"
        ).annotate(universe_name_2=Value("Restaurants", models.CharField())).values(
            "customer__os_name",
            "universe_name_2"
        )

    fast_foods = Order.objects.filter(
            universe_name__icontains="fast food",
            odoo_order_state="done"
        ).annotate(universe_name_2=Value("Fast Food", models.CharField())).values(
            "customer__os_name",
            "universe_name_2"
        )

    breakfast = Order.objects.filter(
            universe_name__icontains="petit",
            odoo_order_state="done"
    ).annotate(universe_name_2=Value("Petits-Déjeuners", models.CharField())).values(
        "customer__os_name",
        "universe_name_2"
    )

    market = Order.objects.filter(
            universe_name__icontains="course",
            odoo_order_state="done"
    ).annotate(universe_name_2=Value("Courses et Marché", models.CharField())).values(
        "customer__os_name",
        "universe_name_2"
    )

    order_data_restaurants = pd.DataFrame.from_records(
        restaurants
    )

    order_data_fast_foods = pd.DataFrame.from_records(
        fast_foods
    )

    order_data_breakfast = pd.DataFrame.from_records(
        breakfast
    )

    order_data_market = pd.DataFrame.from_records(
        market
    )

    order_data = order_data_restaurants.append(
        order_data_fast_foods
    ).append(
        order_data_breakfast
    ).append(
        order_data_market
    )

    sns.catplot(
        y="universe_name_2",
        hue="customer__os_name",
        kind="count",
        palette="pastel",
        edgecolor=".6",
        data=order_data
    )

    plt.show()

    return


def orba_data():

    restaurants = Order.objects.filter(
            universe_name__icontains="restaurant",
            odoo_order_state="done",
            basket_amount__lt=80,
        ).annotate(universe_name_2=Value("Restaurants", models.CharField())).values(
            "basket_amount",
            "universe_name_2"
        )

    fast_foods = Order.objects.filter(
            universe_name__icontains="fast food",
            odoo_order_state="done",
            basket_amount__lt=80,
        ).annotate(universe_name_2=Value("Fast Food", models.CharField())).values(
            "basket_amount",
            "universe_name_2"
        )

    breakfast = Order.objects.filter(
            universe_name__icontains="petit",
            odoo_order_state="done",
            basket_amount__lt=80,
    ).annotate(universe_name_2=Value("Petits-Déjeuners", models.CharField())).values(
        "basket_amount",
        "universe_name_2"
    )

    market = Order.objects.filter(
            universe_name__icontains="course",
            odoo_order_state="done",
            basket_amount__lt=80,
    ).annotate(universe_name_2=Value("Courses et Marché", models.CharField())).values(
        "basket_amount",
        "universe_name_2"
    )

    order_data_restaurants = pd.DataFrame.from_records(
        restaurants
    )

    order_data_fast_foods = pd.DataFrame.from_records(
        fast_foods
    )

    order_data_breakfast = pd.DataFrame.from_records(
        breakfast
    )

    order_data_market = pd.DataFrame.from_records(
        market
    )

    order_data = order_data_restaurants.append(
        order_data_fast_foods
    ).append(
        order_data_breakfast
    ).append(
        order_data_market
    )

    sns.violinplot(
        x="universe_name_2",
        y="basket_amount",
        data=order_data,
    )

    plt.show()

    return


