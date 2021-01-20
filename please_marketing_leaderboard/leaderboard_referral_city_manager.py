# coding: utf-8

from please_marketing_app.models import CityManager, Order
from .models import LeaderboardVoucherCityManager
from please_marketing_script_execution.log_script import log_script
from twilio.rest import Client
from datetime import datetime, timedelta
from django.conf import settings
import emoji
import random
import requests
import json
from django.db.models import Q
import sys
import time
import unicodedata
from please_marketing_app.main_scripts.utilities import first_date_of_current_month, last_day_of_current_month, get_month_name
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# from please_marketing_leaderboard.leaderboard_referral_city_manager import *
def retrieve_voucher_code_leaderboard():
    log_script(name="retrieve_voucher_code_leaderboard", status="s")
    for city_manager in CityManager.objects.filter(referral_codes__isnull=False):
        counter = Order.objects.filter(neighborhood=city_manager.neighborhood, odoo_order_state='done', voucher_code__in=city_manager.referral_codes, order_date__gte=first_date_of_current_month(), order_date__lte=last_day_of_current_month()).count()

        if LeaderboardVoucherCityManager.objects.filter(city_manager=city_manager, end_of_period_date=last_day_of_current_month()).count() == 0:
            LeaderboardVoucherCityManager(
                city_manager=city_manager,
                counter=counter,
                score=0 if counter == 0 else float(float(counter) / float(city_manager.neighborhood.inhabitants_number)),
                end_of_period_date=last_day_of_current_month(),
            ).save()

        elif LeaderboardVoucherCityManager.objects.filter(city_manager=city_manager, end_of_period_date=last_day_of_current_month()).count() == 1:
            leaderboard = LeaderboardVoucherCityManager.objects.get(city_manager=city_manager, end_of_period_date=last_day_of_current_month())

            leaderboard.counter = counter
            leaderboard.score = 0 if counter == 0 else float(float(counter) / float(city_manager.neighborhood.inhabitants_number))
            leaderboard.save()

    max_score = LeaderboardVoucherCityManager.objects.filter(end_of_period_date=last_day_of_current_month()).order_by("-score").first().score

    for city_manager in CityManager.objects.filter(referral_codes__isnull=False):

        # Update score in relative ranking (100%)
        leaderboard = LeaderboardVoucherCityManager.objects.get(city_manager=city_manager, end_of_period_date=last_day_of_current_month())
        leaderboard.score = float(leaderboard.score) / float(max_score) * 100
        leaderboard.save()

    log_script(name="retrieve_voucher_code_leaderboard", status="d")
    return


def send_leaderboard_results():
    log_script(name="send_leaderboard_results", status="s")

    first_date_of_current_period = first_date_of_current_month()
    end_date_of_previous_period = first_date_of_current_period - timedelta(days=1)

    leaderboard_results = LeaderboardVoucherCityManager.objects.filter(end_of_period_date=end_date_of_previous_period).order_by("-score")

    month = str("d'" + str(get_month_name(month_code=end_date_of_previous_period.month))) if str(get_month_name(month_code=end_date_of_previous_period.month))[0] in ["A", "O", "a", "o"] else str("de " + str(get_month_name(month_code=end_date_of_previous_period.month)))

    mail_list = ["contact@pleaseapp.com"]

    for city_manager in CityManager.objects.filter(referral_codes__isnull=False):
        mail_list.append(str(city_manager.email))

    msg = EmailMessage(
        str("[RÉSULTATS LEADERBOARD 🏆] Résultats mois " + str(month)),
        str(render_to_string('please_marketing_leaderboard/email_templates/email_leaderboard_results',
                             {'month': str(month),
                              'leaderboard_results': leaderboard_results,
                              })),
        "Please <contact@pleaseapp.com>",
        mail_list,
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    print("SUCCESS: Leaderboard Results Email properly sent!")

    log_script(name="send_leaderboard_results", status="d")
    return
