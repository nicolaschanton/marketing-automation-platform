# -*- coding: utf-8 -*-
from please_marketing_app.models import Order, Merchant, Customer, NotificationHistory, SmsHistory, EmailHistory
from django.db.models import Count
from django.conf import settings
from datetime import datetime, timedelta, date


# from please_marketing_app.main_scripts.utilities import *
def strike_price(text):
    result = ''
    for c in text:
        if c == ".":
            result = result + c.replace(".", ",")
        else:
            result = result + c + '\u0336'
    return result


def get_short_url_comment_request(medium):
    if medium == "facebook":
        return "https://goo.gl/8ER6JR"
    elif medium == "app_store":
        return "https://goo.gl/g3Hi9k"
    elif medium == "play_store":
        return "https://goo.gl/jXiEyC"
    else:
        return "https://goo.gl/AQigfu"


def first_date_of_current_month():
    today_date = date.today()
    result_date = today_date.replace(day=1)
    return result_date


def last_day_of_current_month():
    today_date = date.today()
    last_days = [31, 30, 29, 28, 27]

    for i in last_days:
        try:
            end = datetime(today_date.year, today_date.month, i)
        except ValueError:
            continue
        else:
            return end.date()

    return None


def get_month_name(month_code):
    if int(month_code) == 1:
        return "Janvier"
    elif int(month_code) == 2:
        return "Février"
    elif int(month_code) == 3:
        return "Mars"
    elif int(month_code) == 4:
        return "Avril"
    elif int(month_code) == 5:
        return "Mai"
    elif int(month_code) == 6:
        return "Juin"
    elif int(month_code) == 7:
        return "Juillet"
    elif int(month_code) == 8:
        return "Août"
    elif int(month_code) == 9:
        return "Septembre"
    elif int(month_code) == 10:
        return "Octobre"
    elif int(month_code) == 11:
        return "Novembre"
    elif int(month_code) == 12:
        return "Décembre"


def get_good_sender(customer):
    if customer.neighborhood.mw_id in [505, 605, 655]:
        response = str(settings.TWILIO_PHONE_PLAIN)

    else:
        response = str(settings.TWILIO_PHONE)

    return response


def has_not_received_too_many_communications(customer):

    notif_counter = NotificationHistory.objects.filter(
        customer=customer,
        send_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=2)).strftime("%s"))),
    ).count()

    sms_counter = SmsHistory.objects.filter(
        customer=customer,
        send_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=30)).strftime("%s"))),
    ).count()

    email_counter = EmailHistory.objects.filter(
        customer=customer,
        send_date__gt=datetime.fromtimestamp(float((datetime.today() - timedelta(days=3)).strftime("%s"))),
    ).count()

    if (notif_counter + sms_counter + email_counter) == 0:
        response = True

    else:
        response = False

    return response


def is_mobile(http_request):

    rsp = True if "Mobile" in http_request.META.get('HTTP_USER_AGENT') else False

    return rsp
