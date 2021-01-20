# -*- coding: utf-8 -*-

from please_marketing_app.models import Customer, Order, OrderLine, Neighborhood, IntercomEvent, Fete, FullContactApi
import requests
from django.db.models import Sum
import os
import sys
from django.conf import settings
import urllib
from django.db.models import Avg, Sum
import datetime
from pytz import timezone
from geopy.geocoders import Nominatim
import json
from please_marketing_app.models import Customer, Fete
from twilio.rest import Client
import datetime
from django.conf import settings
from .anonymous.proxy_rotate import get_proxy
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor


# from please_marketing_referral_program.tests import *
# from please_marketing_referral_program.main_scripts.intercom import *
# from please_marketing_referral_program.main_scripts.amplitude import *
# from please_marketing_referral_program.main_scripts.cos_sim import *
# from please_marketing_referral_program.main_scripts.load_tests_please import *
# from please_marketing_referral_program.main_scripts.erp import *
# from please_marketing_referral_program.main_scripts.referral_program import *
# from please_marketing_referral_program.main_scripts.marketing import *
# from please_marketing_referral_program.main_scripts.local_send_notif import *
# from please_marketing_referral_program.main_scripts.local_send_sms import *
# from please_marketing_referral_program.main_scripts.sms_campaign import *
# from please_marketing_referral_program.main_scripts.utilities import *
# from please_marketing_referral_program.main_scripts.abandoned_cart import *
# from please_marketing_referral_program.main_scripts.activate_rookies import *
# from please_marketing_referral_program.main_scripts.slipping_away import *
# from please_marketing_referral_program.main_scripts.deduplicate import *
# from please_marketing_referral_program.main_scripts.nps import *
# from please_marketing_referral_program.main_scripts.retrieve_vb1_data import *
# from please_marketing_referral_program.models import Order, Customer, IntercomEvent, Merchant, NetPromoterScore, VectorBooking
# python3 manage.py shell --settings=please_marketing.settings_dev
# from please_marketing_referral_program.main_scripts.leaderboard_referral_city_manager import *
# from please_marketing_referral_program.main_scripts.comment_request import *
